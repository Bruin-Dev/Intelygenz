import json
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta

from pytz import utc
from shortuuid import uuid
from src.application import AffectingTroubles
from src.application.repositories import nats_error_response
from src.velocloud_bridge.app import VelocloudBridge


class VelocloudRepository:
    def __init__(self, logger, config, utils_repository):
        self._logger = logger
        self._config = config
        self._utils_repository = utils_repository
        self._velocloud_bridge = VelocloudBridge(logger=logger)

    async def get_links_metrics_by_host(self, host: str, interval: dict) -> dict:
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                "host": host,
                "interval": {
                    "start": interval["start"].isoformat(),
                    "end": interval["end"].isoformat(),
                },
            },
        }

        try:
            self._logger.info(
                f"Getting links metrics between {interval['start']} and {interval['end']} "
                f"from Velocloud host {host}..."
            )
            response = await self._velocloud_bridge.get_links_metric_info(request)
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
                "start_date": past_moment.isoformat(),
                "end_date": now.isoformat(),
            },
        }

        try:
            self._logger.info(
                f"Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} "
                f"that took place between {past_moment} and {now} from Velocloud..."
            )
            response = await self._velocloud_bridge.report_enterprise_event(request)
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
                    f"in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)

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
                        self._logger.info(f"No edge in the customer cache matched edge name. Skipping...")
                        continue

                    serial = matching_edge["serial_number"]
                    self._logger.info(f"Event with matches edge from customer cache with serial number {serial}")

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

    async def get_all_edges(self):
        self._logger.info("Claiming edges for the hosts specified in the config...")
        edge_list = await self._get_all_velo_edges()
        ha_edges = []

        for edge in edge_list:
            if not edge.get("ha_serial_number"):
                continue

            ha_edge = deepcopy(edge)
            ha_edge["serial_number"] = edge["ha_serial_number"]
            ha_edge["ha_serial_number"] = edge["serial_number"]
            ha_edges.append(ha_edge)

        edge_list.extend(ha_edges)
        return edge_list

    async def _get_all_velo_edges(self):
        self._logger.info("Getting list of all velo edges")
        edge_list = await self._get_edges()
        self._logger.info(f"Got all edges from all velos")
        self._logger.info("Getting list of logical IDs by each velo edge")
        logical_ids_by_edge_list = await self._get_logical_id_by_edge_list(edge_list)
        self._logger.info(f"Got all logical IDs by each velo edge")

        self._logger.info(f"Mapping edges to serials...")
        edges_with_serial = self._get_all_serials(edge_list, logical_ids_by_edge_list)
        self._logger.info(f"Amount of edges: {len(edges_with_serial)}")
        edges_with_config = []
        for edge in edges_with_serial:
            edges_with_config.append(await self.add_edge_config(edge))
        self._logger.info(f"Finished building velos + serials map")

        return edges_with_config

    async def _get_edges(self):
        edge_links_list = await self._get_all_edges_links()
        return self._extract_edge_info(edge_links_list)

    async def _get_all_edges_links(self):
        all_edges = []

        for host in self._config.VELOCLOUD_HOSTS:
            response = await self._get_edges_links_by_host(host=host)
            if response["status"] not in range(200, 300):
                self._logger.info(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response["body"]

        return all_edges

    async def _get_edges_links_by_host(self, host):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"host": host},
        }

        try:
            self._logger.info(f"Getting edges links from Velocloud for host {host}...")
            response = await self._velocloud_bridge.get_links_with_edge_info(request)
            self._logger.info("Got edges links from Velocloud!")
        except Exception as e:
            err_msg = f"An error occurred when requesting edge list from {host} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving edges links in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)

        return response

    def _extract_edge_info(self, links_with_edge_info: list) -> list:
        edges_by_serial = {}
        for link in links_with_edge_info:
            velocloud_host = link["host"]
            enterprise_name = link["enterpriseName"]
            enterprise_id = link["enterpriseId"]
            edge_state = link["edgeState"]
            serial_number = link["edgeSerialNumber"]

            if edge_state is None:
                self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if edge_state == "NEVER_ACTIVATED":
                self._logger.info(
                    f"Edge {link['edgeId']} in host {velocloud_host} and enterprise {enterprise_name}"
                    f"(ID: {enterprise_id}) has never been activated. Skipping..."
                )
                continue

            edge_full_id = {"host": link["host"], "enterprise_id": enterprise_id, "edge_id": link["edgeId"]}
            blacklist_edges = self._config.MONITOR_CONFIG["blacklisted_edges"]
            if edge_full_id in blacklist_edges:
                self._logger.info(
                    f"Edge {json.dumps(edge_full_id)} (serial: {serial_number}) is in blacklist. Skipping..."
                )
                continue

            edge = {
                "enterpriseName": link["enterpriseName"],
                "enterpriseId": link["enterpriseId"],
                "enterpriseProxyId": link["enterpriseProxyId"],
                "enterpriseProxyName": link["enterpriseProxyName"],
                "edgeState": link["edgeState"],
                "edgeSystemUpSince": link["edgeSystemUpSince"],
                "edgeServiceUpSince": link["edgeServiceUpSince"],
                "edgeLastContact": link["edgeLastContact"],
                "edgeId": link["edgeId"],
                "edgeSerialNumber": link["edgeSerialNumber"],
                "edgeHASerialNumber": link["edgeHASerialNumber"],
                "edgeModelNumber": link["edgeModelNumber"],
                "edgeLatitude": link["edgeLatitude"],
                "edgeLongitude": link["edgeLongitude"],
                "host": link["host"],
            }

            edges_by_serial.setdefault(serial_number, edge)

        edges = list(edges_by_serial.values())
        return edges

    async def _get_logical_id_by_edge_list(self, edge_list):
        host_to_enterprise_id = {}
        for edge in edge_list:
            host = edge["host"]
            host_to_enterprise_id.setdefault(host, set())
            host_to_enterprise_id[host].add(edge["enterpriseId"])

        logical_id_by_edge_full_id_list = []
        for host in host_to_enterprise_id:
            for enterprise in host_to_enterprise_id[host]:
                enterprise_edge_list = await self._get_all_enterprise_edges(host, enterprise)
                if enterprise_edge_list["status"] not in range(200, 300):
                    self._logger.error(f"Error could not get enterprise edges of enterprise {enterprise}")
                    continue
                for edge in enterprise_edge_list["body"]:
                    edge_full_id_and_logical_id = {
                        "host": host,
                        "enterprise_id": enterprise,
                        "edge_id": edge["id"],
                        "logical_id": [],
                    }
                    for link in edge["links"]:
                        logical_id_dict = {"interface_name": link["interface"], "logical_id": link["logicalId"]}
                        edge_full_id_and_logical_id["logical_id"].append(logical_id_dict)
                    logical_id_by_edge_full_id_list.append(edge_full_id_and_logical_id)

        return logical_id_by_edge_full_id_list

    async def _get_all_enterprise_edges(self, host, enterprise_id):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"host": host, "enterprise_id": enterprise_id},
        }

        try:
            self._logger.info(f"Getting all edges from Velocloud host {host} and enterprise ID {enterprise_id}...")
            response = await self._velocloud_bridge.enterprise_edge_list(request)
            self._logger.info(f"Got all edges from Velocloud host {host} and enterprise ID {enterprise_id}!")
        except Exception as e:
            err_msg = (
                f"An error occurred when requesting edge list from host {host} and enterprise "
                f"ID {enterprise_id} -> {e}"
            )
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving edge list in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            self._logger.error(err_msg)

        return response

    @staticmethod
    def _get_all_serials(edge_list, logical_ids_by_edge_list):
        edges_with_serials = []

        for edge in edge_list:
            edge_full_id = {"host": edge["host"], "enterprise_id": edge["enterpriseId"], "edge_id": edge["edgeId"]}
            serial_number = edge.get("edgeSerialNumber")
            ha_serial_number = edge.get("edgeHASerialNumber")
            last_contact = edge.get("edgeLastContact")
            edge_name = edge.get("edgeName")

            logical_id_list = next(
                (
                    logical_id_edge
                    for logical_id_edge in logical_ids_by_edge_list
                    if logical_id_edge["host"] == edge["host"]
                    if logical_id_edge["enterprise_id"] == edge["enterpriseId"]
                    if logical_id_edge["edge_id"] == edge["edgeId"]
                ),
                None,
            )
            logical_id = []
            if logical_id_list is not None:
                logical_id = logical_id_list["logical_id"]

            edges_with_serials.append(
                {
                    "edge": edge_full_id,
                    "edge_name": edge_name,
                    "serial_number": serial_number,
                    "ha_serial_number": ha_serial_number,
                    "last_contact": last_contact,
                    "logical_ids": logical_id,
                }
            )

        return edges_with_serials

    async def add_edge_config(self, edge):
        edge["links_configuration"] = []

        edge_request = edge["edge"]
        configuration_response = await self.get_links_configuration(edge_request)
        if configuration_response["status"] not in range(200, 300):
            self._logger.error(f"Error while getting links configuration for edge {edge_request}")
            return edge

        for link in configuration_response["body"]:
            edge["links_configuration"].append(
                {
                    "interfaces": link["interfaces"],
                    "mode": link["mode"],
                    "type": link["type"],
                }
            )
        return edge

    async def get_links_configuration(self, edge):
        err_msg = None

        request = {"request_id": uuid(), "body": edge}

        try:
            self._logger.info(f"Getting links configuration for edge {edge}...")
            response = await self._velocloud_bridge.links_configuration(request)
        except Exception as e:
            err_msg = f"An error occurred when requesting links configuration for edge {edge} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving links configuration for edge {edge} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
                )
            else:
                self._logger.info(f"Got links configuration for edge {edge}!")

        if err_msg:
            self._logger.error(err_msg)

        return response
