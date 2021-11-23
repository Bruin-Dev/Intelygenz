from datetime import datetime, timedelta

from application.repositories import nats_error_response
from pytz import utc
from shortuuid import uuid


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def _get_enterprise_events(self, enterprise_id, from_: datetime, to: datetime):
        err_msg = None

        event_types = ['EDGE_DOWN', 'LINK_DEAD']

        request = {
            'request_id': uuid(),
            'body': {
                'enterprise_id': enterprise_id,
                'host': self._config.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
                'start_date': from_,
                'end_date': to,
                'filter': event_types,
            },
        }

        try:
            self._logger.info(
                f"Getting events of enterprise id {enterprise_id} having any type of {event_types} that took place "
                f"between {from_} and {to} from Velocloud..."
            )
            response = await self._event_bus.rpc_request("alert.request.event.enterprise", request, timeout=180)
            self._logger.info(
                f"Got events of enterprise id {enterprise_id} having any type in {event_types} that took place "
                f"between {from_} and {to} from Velocloud!"
            )
        except Exception as e:
            err_msg = f'An error occurred when requesting edge events from Velocloud for enterprise ' \
                      f'id {enterprise_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving events of enterprise id {enterprise_id} having any type '
                    f'in {event_types} that took place between {from_} and {to} '
                    f'in {self._config.BOUNCING_DETECTOR_CONFIG["environment"].upper()}'
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_last_enterprise_events(self, enterprise):
        current_datetime = datetime.now(utc)
        since = current_datetime - timedelta(minutes=self._config.BOUNCING_DETECTOR_CONFIG['past_events_minutes'])
        return await self._get_enterprise_events(enterprise, from_=since, to=current_datetime)

    async def _get_links_metrics(self, host: str, interval: dict) -> dict:
        err_msg = None

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
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving links metrics in {self._config.ENVIRONMENT_NAME.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_last_link_metrics(self):
        current_datetime = datetime.now(utc)
        since = current_datetime - timedelta(minutes=self._config.BOUNCING_DETECTOR_CONFIG['past_events_minutes'])
        scan_interval_for_metrics = {
            'start': since,
            'end': current_datetime,
        }
        return await self._get_links_metrics(self._config.BOUNCING_DETECTOR_CONFIG['velocloud_host'],
                                             scan_interval_for_metrics)
