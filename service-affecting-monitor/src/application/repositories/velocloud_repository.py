from datetime import datetime
from datetime import timedelta

from pytz import utc
from shortuuid import uuid

from application.repositories import nats_error_response


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_links_metrics_by_host(self, host: str, interval: dict) -> dict:
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

    async def get_all_links_metrics(self, interval: dict) -> dict:
        velocloud_hosts = set(
            edge['host']
            for edge in self._config.MONITOR_CONFIG['device_by_id']
        )

        all_links_metrics = []
        for host in velocloud_hosts:
            response = await self.get_links_metrics_by_host(host=host, interval=interval)
            if response['status'] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve links metrics from Velocloud host {host}")
                continue
            all_links_metrics += response['body']

        return_response = {
            "request_id": uuid(),
            'body': all_links_metrics,
            'status': 200,
        }
        return return_response

    async def get_links_metrics_for_latency_checks(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['latency'])

        scan_interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_packet_loss_checks(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(
            minutes=self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['packet_loss']
        )

        scan_interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_jitter_checks(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['jitter'])

        scan_interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_bandwidth_checks(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(
            minutes=self._config.MONITOR_CONFIG['monitoring_minutes_per_trouble']['bandwidth']
        )

        scan_interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_autoresolve(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(
            minutes=self._config.MONITOR_CONFIG['autoresolve']['metrics_lookup_interval_minutes']
        )

        interval_for_metrics = {
            'start': past_moment,
            'end': now,
        }
        return await self.get_all_links_metrics(interval=interval_for_metrics)
