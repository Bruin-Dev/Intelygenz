from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from datetime import datetime, timedelta
from shortuuid import uuid
from datetime import datetime, timedelta
from pytz import utc


from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from shortuuid import uuid


class StoreLinkMetrics:

    def __init__(self, logger, config, event_bus, mongo_client, scheduler):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._mongo_client = mongo_client
        self._scheduler = scheduler

    async def start_links_metrics_collector(self):
        self._logger.info('Scheduling links metrics collector job...')
        tz = timezone(self._config.SCHEDULER_TIMEZONE)
        next_run_time = datetime.now(tz)
        try:
            self._scheduler.add_job(self._store_links_metrics_of_config_velos, 'interval',
                                    minutes=self._config.STORING_INTERVAL_MINUTES,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_links_metrics_collector_job')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of links metrics collector job. Reason: {conflict}')

    async def _store_links_metrics_of_config_velos(self):
        self._logger.info(f"Getting all links metrics for velos: {self._config.VELO_HOSTS}")
        created_date = datetime.utcnow().isoformat()

        for velo in self._config.VELO_HOSTS:
            links_metrics = await self._get_links_metrics_of_one_velo(velo)
            self._logger.info(f"Got all links metrics for velo: {velo}")
            insert_data = {"velo": velo, "metrics": links_metrics["body"], "created_date": created_date}
            self._mongo_client.insert(insert_data)
        self._logger.info(f"Stored all links metrics for the velos: {self._config.VELO_HOSTS}")

    async def _get_links_metrics_of_one_velo(self, host):
        err_msg = None
        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.STORING_INTERVAL_MINUTES)
        interval = {
            'start': past_moment,
            'end': now,
        }

        request = {
            "request_id": uuid(),
            "body": {
                'host': host,
                'interval': interval,
            },
        }

        try:
            self._logger.info(
                f"Getting links metrics between {interval['start']} and {interval['end']} "
                f"from Velocloud host {host}..."
            )
            response = await self._event_bus.rpc_request("get.links.metric.info", request, timeout=30)
            self._logger.info(f"Got links metrics from Velocloud host {host}!")
        except Exception as e:
            err_msg = f'An error occurred when requesting links metrics from Velocloud -> {e}'
            response = None
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving links metrics in {self._config.CURRENT_ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
        self._logger.info(f"Got all links metrics for velo: {host}")
        return response
