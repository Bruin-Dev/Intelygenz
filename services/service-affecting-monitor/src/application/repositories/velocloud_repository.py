from collections import defaultdict
from datetime import datetime, timedelta

from application import AffectingTroubles
from application.repositories import nats_error_response
from pytz import utc
from shortuuid import uuid


class VelocloudRepository:
    def __init__(self, event_bus, logger, config, utils_repository, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._utils_repository = utils_repository
        self._notifications_repository = notifications_repository

    async def get_links_metrics_by_host(self, host: str, interval: dict) -> dict:
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": host,
                "interval": interval,
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
            err_msg = f"An error occurred when requesting links metrics from Velocloud -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving links metrics in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_all_links_metrics(self, interval: dict) -> dict:
        all_links_metrics = []
        for host in self._config.MONITOR_CONFIG["velo_filter"]:
            response = await self.get_links_metrics_by_host(host=host, interval=interval)
            if response["status"] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve links metrics from Velocloud host {host}")
                continue
            all_links_metrics += response["body"]

        return_response = {
            "request_id": uuid(),
            "body": all_links_metrics,
            "status": 200,
        }
        return return_response

    async def get_links_metrics_for_latency_checks(self) -> dict:
        trouble = AffectingTroubles.LATENCY

        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble])

        scan_interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_packet_loss_checks(self) -> dict:
        trouble = AffectingTroubles.PACKET_LOSS

        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble])

        scan_interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_jitter_checks(self) -> dict:
        trouble = AffectingTroubles.JITTER

        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble])

        scan_interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_bandwidth_checks(self) -> dict:
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION

        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble])

        scan_interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_bouncing_checks(self) -> dict:
        trouble = AffectingTroubles.BOUNCING

        now = datetime.now(utc)
        past_moment = now - timedelta(minutes=self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble])

        scan_interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=scan_interval_for_metrics)

    async def get_links_metrics_for_autoresolve(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(
            minutes=self._config.MONITOR_CONFIG["autoresolve"]["metrics_lookup_interval_minutes"]
        )

        interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=interval_for_metrics)

    async def get_links_metrics_for_bandwidth_reports(self) -> dict:
        now = datetime.now(utc)
        past_moment = now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"])

        interval_for_metrics = {
            "start": past_moment,
            "end": now,
        }
        return await self.get_all_links_metrics(interval=interval_for_metrics)

    async def get_enterprise_events(self, host, enterprise_id):
        err_msg = None
        now = datetime.now(utc)
        minutes = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][AffectingTroubles.BOUNCING]
        past_moment = now - timedelta(minutes=minutes)
        event_types = ["LINK_DEAD"]

        request = {
            "request_id": uuid(),
            "body": {
                "host": host,
                "enterprise_id": enterprise_id,
                "filter": event_types,
                "start_date": past_moment,
                "end_date": now,
            },
        }

        try:
            self._logger.info(
                f"Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} "
                f"that took place between {past_moment} and {now} from Velocloud..."
            )
            response = await self._event_bus.rpc_request("alert.request.event.enterprise", request, timeout=180)
        except Exception as e:
            err_msg = (
                f"An error occurred when requesting edge events from Velocloud for host {host} "
                f"and enterprise id {enterprise_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status in range(200, 300):
                self._logger.info(
                    f"Got events of host {host} and enterprise id {enterprise_id} having any type in {event_types} "
                    f"that took place between {past_moment} and {now} from Velocloud!"
                )
            else:
                err_msg = (
                    f"Error while retrieving events of host {host} and enterprise id {enterprise_id} having any type "
                    f"in {event_types} that took place between {past_moment} and {now} "
                    f"in {self._config.ENVIRONMENT_NAME.upper()}"
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_events_by_serial_and_interface(self, customer_cache):
        edges_by_host_and_enterprise = self._structure_edges_by_host_and_enterprise(customer_cache)
        events = defaultdict(lambda: defaultdict(list))

        for host in edges_by_host_and_enterprise:
            edges_by_enterprise = edges_by_host_and_enterprise[host]

            for enterprise_id in edges_by_enterprise:
                edges = edges_by_enterprise[enterprise_id]
                enterprise_events_response = await self.get_enterprise_events(host, enterprise_id)
                enterprise_events = enterprise_events_response["body"]

                if enterprise_events_response["status"] not in range(200, 300):
                    continue

                for event in enterprise_events:
                    matching_edge = self._utils_repository.get_first_element_matching(
                        edges, lambda edge: edge["edge_name"] == event["edgeName"]
                    )
                    if not matching_edge:
                        self._logger.info(
                            f'No edge in the customer cache had edge name {event["edgeName"]}. Skipping...'
                        )
                        continue

                    serial = matching_edge["serial_number"]
                    self._logger.info(
                        f'Event with edge name {event["edgeName"]} matches edge from customer cache with'
                        f"serial number {serial}"
                    )

                    interface = self._utils_repository.get_interface_from_event(event)
                    events[serial][interface].append(event)

        return events

    def _structure_edges_by_host_and_enterprise(self, customer_cache):
        self._logger.info("Organizing customer cache by host and enterprise_id")
        edges = defaultdict(lambda: defaultdict(list))

        for edge in customer_cache:
            host = edge["edge"]["host"]
            enterprise_id = edge["edge"]["enterprise_id"]
            edges[host][enterprise_id].append(edge)

        return edges

    def filter_links_metrics_by_client(self, links_metrics, client_id, customer_cache):
        filtered_links_metrics = []

        for link_metrics in links_metrics:
            edge_full_id = {
                "host": link_metrics["link"]["host"],
                "enterprise_id": link_metrics["link"]["enterpriseId"],
                "edge_id": link_metrics["link"]["edgeId"],
            }

            matching_edge = self._utils_repository.get_first_element_matching(
                customer_cache,
                lambda edge: edge["edge"] == edge_full_id,
            )

            if matching_edge and matching_edge["bruin_client_info"]["client_id"] == client_id:
                filtered_links_metrics.append(link_metrics)

        return filtered_links_metrics
