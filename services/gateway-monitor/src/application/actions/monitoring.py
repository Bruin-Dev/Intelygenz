import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List

from application.dataclasses import Gateway, GatewayList, GatewayPair
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class Monitor:
    def __init__(
        self,
        event_bus,
        logger,
        scheduler,
        config,
        servicenow_repository,
        velocloud_repository,
        notifications_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._servicenow_repository = servicenow_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository

    async def start_monitoring(self, exec_on_start: bool):
        self._logger.info("Scheduling Gateway Monitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info("Gateway Monitor job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._monitoring_process,
                "interval",
                seconds=self._config.MONITOR_CONFIG["monitoring_job_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_monitor_process",
            )
        except ConflictingIdError as conflict:
            self._logger.info(f"Skipping start of Gateway Monitoring job. Reason: {conflict}")

    async def _monitoring_process(self):
        start = time.time()
        self._logger.info(f"Starting Gateway Monitoring process!")

        monitor_tasks = [
            self._tunnel_count_check(host) for host in self._config.MONITOR_CONFIG["monitored_velocloud_hosts"]
        ]
        await asyncio.gather(*monitor_tasks, return_exceptions=True)

        stop = time.time()
        self._logger.info(
            f"Gateway Monitoring process finished! Elapsed time: " f"{round((stop - start) / 60, 2)} minutes"
        )

    async def _tunnel_count_check(self, host: str):
        self._logger.info(f"Checking network gateway status in Velocloud host {host}...")

        first_lookup_interval = datetime.now() - timedelta(
            seconds=self._config.MONITOR_CONFIG["gateway_lookup_intervals"]["first_lookup"]
        )
        gateway_status_first_interval = await self._velocloud_repository.get_network_gateway_status_list(
            host, since=first_lookup_interval.strftime("%Y-%m-%d %H:%M:%S"), metrics=["tunnelCount"]
        )
        if gateway_status_first_interval["status"] not in range(200, 300):
            self._logger.error(f"An error occurred while trying to get gateway status for the first interval")
            return
        gateway_status_first_interval = gateway_status_first_interval["body"]

        second_lookup_interval = datetime.now() - timedelta(
            seconds=self._config.MONITOR_CONFIG["gateway_lookup_intervals"]["second_lookup"]
        )
        gateway_status_second_interval = await self._velocloud_repository.get_network_gateway_status_list(
            host, since=second_lookup_interval.strftime("%Y-%m-%d %H:%M:%S"), metrics=["tunnelCount"]
        )
        if gateway_status_second_interval["status"] not in range(200, 300):
            self._logger.error(f"An error occurred while trying to get gateway status for the second interval")
            return
        gateway_status_second_interval = gateway_status_second_interval["body"]

        gateway_pairs = self._build_pair_statuses(gateway_status_first_interval, gateway_status_second_interval)
        unhealthy_gateways = self._check_average_tunnel_count(gateway_pairs)
        if unhealthy_gateways:
            self._logger.info(f"{len(unhealthy_gateways.args)} unhealthy gateways found!")
            servicenow_tasks = [
                self._check_servicenow(unhealthy_gateway) for unhealthy_gateway in unhealthy_gateways.args
            ]
            out = await asyncio.gather(*servicenow_tasks, return_exceptions=True)
            for ex in filter(None, out):
                self._logger.error(f"Error while attempting ServiceNow check for unhealthy gateway: {ex}")
            self._logger.info(f"unhealthy gateway were processed...")
        else:
            self._logger.info(f"no unhealthy gateways were found")

    def _build_pair_statuses(
        self, gateway_status_first_interval: GatewayList, gateway_status_second_interval: GatewayList
    ) -> GatewayPair:
        first_lookup_gateways_by_id = {gw.id: gw for gw in gateway_status_first_interval.args}
        second_lookup_gateways_by_id = {gw.id: gw for gw in gateway_status_second_interval.args}

        first_lookup_gateways = []
        second_lookup_gateways = []
        for id_, gw_first in first_lookup_gateways_by_id.items():
            gw_second = second_lookup_gateways_by_id.get(id_)
            if gw_second is None:
                self._logger.warning(
                    f"Gateway {id_} from host {gw_first.host} was not found in one of the lookups. Skipping..."
                )
                continue

            first_lookup_gateways.append(
                Gateway(
                    host=gw_first.host,
                    id=id_,
                    tunnel_count=gw_first.tunnel_count,
                )
            )
            second_lookup_gateways.append(
                Gateway(
                    host=gw_first.host,
                    id=id_,
                    tunnel_count=gw_second.tunnel_count,
                )
            )
        result = GatewayPair(GatewayList(*first_lookup_gateways), GatewayList(*second_lookup_gateways))

        return result

    def _check_average_tunnel_count(self, gateway_pairs: GatewayPair) -> GatewayList:
        unhealthy_gateways = []
        for first, second in zip(gateway_pairs.first_tunnel_count.args, gateway_pairs.second_tunnel_count.args):
            if self._tunnel_count_less(first.tunnel_count, second.tunnel_count):
                unhealthy_gateways.append(second)
        result = GatewayList(*unhealthy_gateways)
        return result

    def _tunnel_count_less(self, first_tunnel_count: int, second_tunnel_count: int) -> bool:
        percentual_loss = (1 - (second_tunnel_count / first_tunnel_count)) * 100
        return percentual_loss > self._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]

    async def _check_servicenow(self, unhealthy_gateway: Gateway):
        try:
            await self._servicenow_repository.check_active_incident_tickets_for_gateway(unhealthy_gateway)
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to check active incident tickets for gateway "
                f"{unhealthy_gateway.id} -> {e}"
            )
