import time
from datetime import datetime
from typing import Dict, List, Tuple

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
        gateway_lookup_intervals = self._config.MONITOR_CONFIG["gateway_lookup_intervals"]

        # Get gateways info
        network_gateway_list_response = await self._velocloud_repository.get_network_gateway_list(host)
        if network_gateway_list_response["status"] not in range(200, 300):
            return

        # Group gateways by ID
        gateways = {}
        for gateway in network_gateway_list_response["body"]:
            gateways[gateway["id"]] = gateway

        # Get first interval
        first_network_gateway_status_list_response = await self._velocloud_repository.get_network_gateway_status_list(
            host, gateway_lookup_intervals["first"]
        )
        if first_network_gateway_status_list_response["status"] not in range(200, 300):
            return
        first_gateway_list = self._map_gateway_info(gateways, first_network_gateway_status_list_response["body"])

        # Get second interval
        second_network_gateway_status_list_response = await self._velocloud_repository.get_network_gateway_status_list(
            host, gateway_lookup_intervals["second"]
        )
        if second_network_gateway_status_list_response["status"] not in range(200, 300):
            return
        second_gateway_list = self._map_gateway_info(gateways, second_network_gateway_status_list_response["body"])

        # Process gateways
        gateway_pairs = self._build_gateway_pairs(host, first_gateway_list, second_gateway_list)
        unhealthy_gateway_pairs = self._get_unhealthy_gateways(gateway_pairs)

        if unhealthy_gateway_pairs:
            self._logger.info(f"{len(unhealthy_gateway_pairs)} unhealthy gateway(s) found for host {host}")
            # TODO: Document incident on ServiceNow for each unhealthy gateway
        else:
            self._logger.info(f"No unhealthy gateways were found for host {host}")

        self._logger.info(f"Finished processing Velocloud host {host}!")

    @staticmethod
    def _map_gateway_info(gateways_by_id: Dict[int, dict], gateway_status_list: List[dict]) -> List[dict]:
        gateways = []

        for gateway_status in gateway_status_list:
            gateway_id = gateway_status.pop("gatewayId")
            gateway = gateways_by_id[gateway_id]
            gateways.append({"id": gateway_id, "name": gateway["name"], **gateway_status})

        return gateways

    def _build_gateway_pairs(
        self, host: str, first_gateway_list: List[dict], second_gateway_list: List[dict]
    ) -> List[Tuple[dict, dict]]:
        gateway_pairs = []
        gateways_without_metrics = []

        first_gateway_names = {gw["name"] for gw in first_gateway_list}
        second_gateway_names = {gw["name"] for gw in second_gateway_list}
        common_gateway_names = first_gateway_names & second_gateway_names
        exclusive_gateway_names = first_gateway_names ^ second_gateway_names

        if exclusive_gateway_names:
            self._logger.warning(
                f"The following gateways from host {host} "
                f"were not found in one of the intervals: {list(exclusive_gateway_names)}"
            )

        for gateway_name in common_gateway_names:
            first_interval_gateway = self._utils_repository.get_first_element_matching(
                first_gateway_list, lambda gw: gw["name"] == gateway_name
            )
            second_interval_gateway = self._utils_repository.get_first_element_matching(
                second_gateway_list, lambda gw: gw["name"] == gateway_name
            )

            if self._has_metrics(first_interval_gateway):
                gateway_pair = (first_interval_gateway, second_interval_gateway)
                gateway_pairs.append(gateway_pair)
            else:
                gateways_without_metrics.append(first_interval_gateway["name"])

        if gateways_without_metrics:
            self._logger.warning(
                f"The following gateways from host {host} "
                f"did not have metrics in the first interval: {gateways_without_metrics}"
            )

        return gateway_pairs

    @staticmethod
    def _has_metrics(gateway: dict) -> bool:
        return gateway["tunnelCount"] > 0

    def _get_unhealthy_gateways(self, gateway_pairs: List[Tuple[dict, dict]]) -> List[Tuple[dict, dict]]:
        return [gw_pair for gw_pair in gateway_pairs if not self._is_tunnel_count_within_threshold(gw_pair)]

    def _is_tunnel_count_within_threshold(self, gateway_pair: Tuple[dict, dict]) -> bool:
        first_tunnel_count = gateway_pair[0]["tunnelCount"]
        second_tunnel_count = gateway_pair[1]["tunnelCount"]

        percentage_decrease = (1 - (second_tunnel_count / first_tunnel_count)) * 100
        return percentage_decrease < self._config.MONITOR_CONFIG["thresholds"]["tunnel_count"]
