import logging
from typing import Any

logger = logging.getLogger(__name__)


class VelocloudRepository:
    def __init__(self, config, velocloud_client):
        self._config = config
        self._velocloud_client = velocloud_client

    async def connect_to_all_hosts(self):
        await self._velocloud_client.schedule_connect_to_all_hosts()

    async def get_all_edge_events(self, edge, start, end, limit, filter_events_status_list):
        logger.info(f"Getting events for edge {edge} between {start} and {end}...")
        body = {
            "enterpriseId": edge["enterprise_id"],
            "interval": {"start": start, "end": end},
            "filter": {"limit": limit},
            "edgeId": [edge["edge_id"]],
        }
        return await self._get_all_events(edge["host"], body, filter_events_status_list)

    async def get_all_enterprise_events(self, enterprise, host, start, end, limit, filter_events_status_list):
        logger.info(f"Getting events from enterprise {enterprise} of host {host} between {start} and {end}")

        body = {"enterpriseId": enterprise, "interval": {"start": start, "end": end}, "filter": {"limit": limit}}

        return await self._get_all_events(host, body, filter_events_status_list)

    async def _get_all_events(self, host, body, filter_events_status_list):
        if filter_events_status_list is not None:
            logger.info(f"Using event type filter {filter_events_status_list} to get all events from host {host}")
            body["filter"]["rules"] = [{"field": "event", "op": "is", "values": filter_events_status_list}]

        logger.info(f"Getting all events from host {host} using filters {body}")
        response = await self._velocloud_client.get_all_events(host, body)

        if response["status"] not in range(200, 300):
            logger.error(f"Could not get all events from {host} using filters {body}. Response: {response}")
            return response

        full_events = response["body"]
        response["body"] = full_events["data"]

        return response

    async def get_all_enterprise_names(self, msg):
        logger.info("Getting all enterprise names")
        enterprises = await self._velocloud_client.get_all_enterprise_names()

        if enterprises["status"] not in range(200, 300):
            logger.error(f"Error {enterprises['status']}, error: {enterprises['body']}")
            return {"body": enterprises["body"], "status": enterprises["status"]}

        enterprise_names = [e["enterprise_name"] for e in enterprises["body"]]

        if len(msg["filter"]) > 0:
            enterprise_names = [
                e_name
                for e_name in enterprise_names
                for filter_enterprise in msg["filter"]
                if e_name == filter_enterprise
            ]

        return {"body": enterprise_names, "status": enterprises["status"]}

    async def get_links_with_edge_info(self, velocloud_host: str):
        links_with_edge_info_response = await self._velocloud_client.get_links_with_edge_info(velocloud_host)

        if links_with_edge_info_response["status"] not in range(200, 300):
            logger.error(
                f"Could not get links with edge info for host {velocloud_host}. Response: "
                f"{links_with_edge_info_response}"
            )
            return links_with_edge_info_response

        for elem in links_with_edge_info_response["body"]:
            elem["host"] = velocloud_host

        return links_with_edge_info_response

    async def get_links_metric_info(self, velocloud_host: str, interval: dict):
        links_metric_info_response = await self._velocloud_client.get_links_metric_info(velocloud_host, interval)

        if links_metric_info_response["status"] not in range(200, 300):
            logger.error(
                f"Could not get links metric info for host {velocloud_host} and interval {interval}. Response: "
                f"{links_metric_info_response}"
            )
            return links_metric_info_response

        for elem in links_metric_info_response["body"]:
            elem["link"]["host"] = velocloud_host

        return links_metric_info_response

    async def get_enterprise_edges(self, host, enterprise_id):
        return await self._velocloud_client.get_enterprise_edges(host, enterprise_id)

    async def get_links_configuration(self, edge_full_id):
        config_response = {}

        config_modules_response = await self._velocloud_client.get_edge_configuration_modules(edge_full_id)
        if config_modules_response["status"] not in range(200, 300):
            logger.error(
                f"Could not get links configuration for edge {edge_full_id}. Response: {config_modules_response}"
            )
            return config_modules_response

        config_modules = config_modules_response["body"]
        config_wan_module = config_modules.get("WAN")
        if not config_wan_module:
            logger.warning(f"No WAN module was found for edge {edge_full_id}")

            config_response["status"] = 404
            config_response["body"] = f"No WAN module was found for edge {edge_full_id}"
            return config_response

        wan_module_data = config_wan_module["data"]
        links_configuration = wan_module_data.get("links")
        if not links_configuration:
            logger.warning(f"No links configuration was found in WAN module of edge {edge_full_id}")

            config_response["status"] = 404
            config_response["body"] = f"No links configuration was found in WAN module of edge {edge_full_id}"
            return config_response

        config_response["status"] = 200
        config_response["body"] = links_configuration

        return config_response

    async def get_edge_links_series(self, host, payload):
        return await self._velocloud_client.get_edge_links_series(host, payload)

    async def get_network_enterprise_edges(self, host: str, enterprise_ids: list[int]) -> dict[str, Any]:
        response = await self._velocloud_client.get_network_enterprises(host, enterprise_ids)
        enterprise_edges_response = dict.fromkeys(["body", "status"])

        if response["status"] not in range(200, 300):
            logger.error(
                f"Could not get network enterprise edges for host {host} and enterprises {enterprise_ids}. Response: "
                f"{enterprise_edges_response}"
            )
            return response

        if not len(response["body"]):
            logger.warning(f"No enterprises found for host {host} and enterprise ids {enterprise_ids}")
            enterprise_edges_response[
                "body"
            ] = f"No enterprises found for host {host} and enterprise ids {enterprise_ids}"
            enterprise_edges_response["status"] = 404

        edges = sum([enterprise_info["edges"] for enterprise_info in response["body"]], [])

        if edges:
            logger.info(f"Found {len(edges)} edges for host {host} and enterprise ids {enterprise_ids}")

            for edge in edges:
                edge["host"] = host
            enterprise_edges_response["body"] = edges
            enterprise_edges_response["status"] = 200
        else:
            logger.warning(f"No edges found for host {host} and enterprise ids {enterprise_ids}")
            enterprise_edges_response["body"] = f"No edges found for host {host} and enterprise ids {enterprise_ids}"
            enterprise_edges_response["status"] = 404

        return enterprise_edges_response

    async def get_network_gateways(self, host: str):
        response = await self._velocloud_client.get_network_gateways(host)

        if response["status"] not in range(200, 300):
            logger.error(f"Could not get network gateways for host {host}. Response: {response}")
            return response

        gateways = []
        for gateway in response["body"]:
            gateways.append(
                {
                    "host": host,
                    "id": gateway["id"],
                    "name": gateway["name"],
                    "status": gateway["gatewayState"],
                }
            )
        response["body"] = gateways

        return response

    async def get_gateway_status_metrics(self, host: str, gateway_id: int, interval: dict, metrics: list[str]):
        return await self._velocloud_client.get_gateway_status_metrics(host, gateway_id, interval, metrics)
