import time
from datetime import datetime
from typing import List

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
        utils_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._servicenow_repository = servicenow_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._utils_repository = utils_repository

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
        self._logger.info(f"Starting Gateway Monitoring process...")

        for host in self._config.MONITOR_CONFIG["monitored_velocloud_hosts"]:
            try:
                await self._process_host(host)
            except Exception as e:
                self._logger.exception(e)

        stop = time.time()
        self._logger.info(f"Gateway Monitoring process finished! Elapsed time: {round((stop - start) / 60, 2)} minutes")

    async def _process_host(self, host: str):
        self._logger.info(f"Processing Velocloud host {host}...")
        network_gateway_list_response = await self._velocloud_repository.get_network_gateway_list(host)

        if network_gateway_list_response["status"] not in range(200, 300):
            return

        gateways = network_gateway_list_response["body"]
        for gateway in gateways:
            try:
                gateway["metrics"] = await self._get_gateway_metrics(gateway)
            except Exception as e:
                self._logger.exception(e)

        gateways = self._filter_gateways_with_metrics(gateways)
        unhealthy_gateways = self._get_unhealthy_gateways(gateways)

        if unhealthy_gateways:
            self._logger.info(f"{len(unhealthy_gateways)} unhealthy gateway(s) found for host {host}")
            for gateway in unhealthy_gateways:
                try:
                    await self._report_servicenow_incident(gateway)
                except Exception as e:
                    self._logger.exception(e)
        else:
            self._logger.info(f"No unhealthy gateways were found for host {host}")

        self._logger.info(f"Finished processing Velocloud host {host}!")

    async def _get_gateway_metrics(self, gateway: dict):
        response = await self._velocloud_repository.get_gateway_status_metrics(gateway)

        if response["status"] not in range(200, 300):
            return None

        return response["body"]

    async def _report_servicenow_incident(self, gateway: dict):
        report_incident_response = await self._servicenow_repository.report_incident(gateway)

        if report_incident_response["status"] not in range(200, 300):
            self._logger.error(
                f"Failed to report incident to ServiceNow for host {gateway['host']} and gateway {gateway['name']}"
            )
            return

        result = report_incident_response["body"]["result"]

        if result["state"] == "inserted":
            self._logger.info(
                f"A new incident with ID {result['number']} was created in ServiceNow "
                f"for host {gateway['host']} and gateway {gateway['name']}"
            )
        elif result["state"] == "ignored":
            self._logger.info(
                f"An open incident with ID {result['number']} already existed in ServiceNow "
                f"for host {gateway['host']} and gateway {gateway['name']}, a note was added to it"
            )
        elif result["state"] == "reopened":
            self._logger.info(
                f"A resolved incident with ID {result['number']} already existed in ServiceNow "
                f"for host {gateway['host']} and gateway {gateway['name']}, it was reopened and a note was added to it"
            )

    def _filter_gateways_with_metrics(self, gateways: List[dict]) -> List[dict]:
        filtered_gateways = []

        for gateway in gateways:
            if self._has_metrics(gateway):
                filtered_gateways.append(gateway)
            else:
                self._logger.warning(f"Gateway {gateway['name']} from host {gateway['host']} has missing metrics")

        return filtered_gateways

    @staticmethod
    def _has_metrics(gateway: dict) -> bool:
        metrics = gateway["metrics"]

        if not metrics:
            return False

        tunnel_count = metrics.get("tunnelCount")
        if not tunnel_count or tunnel_count["average"] == 0:
            return False

        return True

    def _get_unhealthy_gateways(self, gateways: List[dict]) -> List[dict]:
        return [gw for gw in gateways if not self._is_tunnel_count_within_threshold(gw)]

    def _is_tunnel_count_within_threshold(self, gateway: dict) -> bool:
        tunnel_count = gateway["metrics"]["tunnelCount"]
        percentage_decrease = (1 - (tunnel_count["min"] / tunnel_count["average"])) * 100
        return percentage_decrease < self._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]
