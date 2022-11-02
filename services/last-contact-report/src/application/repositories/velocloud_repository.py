import json
import logging

from shortuuid import uuid

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)

nats_error_response = {"body": None, "status": 503}


class VelocloudRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_edges_links_by_host(self, host):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"host": host},
        }

        try:
            logger.info(f"Getting edges links from Velocloud for host {host}...")
            response = await self._nats_client.request("get.links.with.edge.info", to_json_bytes(request), timeout=300)
            response = json.loads(response.data)
            logger.info("Got edges links from Velocloud!")
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
            await self._notify_error(err_msg)

        return response

    async def get_all_edges_links(self):
        all_edges = []
        for host in self._config.REPORT_CONFIG["monitored_velocloud_hosts"]:
            response = await self.get_edges_links_by_host(host=host)
            if response["status"] not in range(200, 300):
                logger.warning(f"Error: could not retrieve edges links by host: {host}")
                continue
            all_edges += response["body"]

        return_response = {"request_id": uuid(), "status": 200, "body": all_edges}
        return return_response

    def extract_edge_info(self, links_with_edge_info: list) -> list:
        edges_by_edge_serial = {}
        for link in links_with_edge_info:
            velocloud_host = link["host"]
            enterprise_name = link["enterpriseName"]
            enterprise_id = link["enterpriseId"]
            edge_name = link["edgeName"]
            serial_number = link["edgeSerialNumber"]

            if link["edgeState"] is None:
                logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if link["edgeState"] == "NEVER_ACTIVATED":
                logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
                continue

            edges_by_edge_serial.setdefault(
                serial_number,
                {
                    "enterpriseName": link["enterpriseName"],
                    "enterpriseId": link["enterpriseId"],
                    "enterpriseProxyId": link["enterpriseProxyId"],
                    "enterpriseProxyName": link["enterpriseProxyName"],
                    "edgeName": link["edgeName"],
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
                },
            )

        edges = list(edges_by_edge_serial.values())
        return edges

    async def get_edges(self):
        edge_links_list = await self.get_all_edges_links()
        return self.extract_edge_info(edge_links_list["body"])

    async def _notify_error(self, err_msg):
        logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
