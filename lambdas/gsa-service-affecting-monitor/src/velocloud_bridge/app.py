import asyncio

from src.velocloud_bridge.clients.velocloud_client import VelocloudClient
from src.velocloud_bridge.repositories.velocloud_repository import VelocloudRepository

missing = object()


class VelocloudBridge:
    def __init__(self, logger):
        self._logger = logger
        self._velocloud_client = VelocloudClient(logger=logger)
        self._velocloud_repository = VelocloudRepository(logger=logger, velocloud_client=self._velocloud_client)

        asyncio.get_event_loop().run_until_complete(self._velocloud_repository.connect_to_all_servers())

    async def get_links_metric_info(self, request: dict):
        request_id = request["request_id"]

        response = {
            "request_id": request_id,
            "body": None,
            "status": None,
        }

        request_body: dict = request.get("body", missing)
        if request_body is missing:
            self._logger.error(f'Cannot get links metric info: "body" is missing in the request')
            response["body"] = 'Must include "body" in the request'
            response["status"] = 400
            return response

        velocloud_host: str = request_body.get("host", missing)
        if velocloud_host is missing:
            self._logger.error(f'Cannot get links metric info: "host" is missing in the body of the request')
            response["body"] = 'Must include "host" and "interval" in the body of the request'
            response["status"] = 400
            return response

        interval: str = request_body.get("interval", missing)
        if interval is missing:
            self._logger.error(f'Cannot get links metric info: "interval" is missing in the body of the request')
            response["body"] = 'Must include "host" and "interval" in the body of the request'
            response["status"] = 400
            return response

        self._logger.info(f'Getting links metric info from Velocloud host "{velocloud_host}"...')
        links_metric_info_response: dict = await self._velocloud_repository.get_links_metric_info(
            velocloud_host, interval
        )

        response = {
            "request_id": request_id,
            **links_metric_info_response,
        }
        return response

    async def report_enterprise_event(self, msg: dict):
        enterprise_event_response = {"request_id": msg["request_id"], "body": None, "status": None}
        if msg.get("body") is None:
            enterprise_event_response["status"] = 400
            enterprise_event_response["body"] = 'Must include "body" in request'
            return enterprise_event_response
        if all(key in msg["body"].keys() for key in ("enterprise_id", "host", "start_date", "end_date")):
            enterprise_id = msg["body"]["enterprise_id"]
            host = msg["body"]["host"]
            start = msg["body"]["start_date"]
            end = msg["body"]["end_date"]
            limit = None
            filter_ = None

            if "filter" in msg["body"].keys():
                filter_ = msg["body"]["filter"]

            if "limit" in msg["body"].keys():
                limit = msg["body"]["limit"]

            self._logger.info(f"Sending events for enterprise with data {enterprise_id} for alerts")
            events_by_enterprise = await self._velocloud_repository.get_all_enterprise_events(
                enterprise_id, host, start, end, limit, filter_
            )
            enterprise_event_response["body"] = events_by_enterprise["body"]
            enterprise_event_response["status"] = events_by_enterprise["status"]

        else:
            enterprise_event_response["status"] = 400
            enterprise_event_response["body"] = (
                'Must include "enterprise_id", "host", "start_date", "end_date" ' "in request"
            )
        return enterprise_event_response

    async def get_links_with_edge_info(self, request: dict):
        request_id = request["request_id"]

        response = {
            "request_id": request_id,
            "body": None,
            "status": None,
        }

        request_body: dict = request.get("body", missing)
        if request_body is missing:
            self._logger.error(f'Cannot get links with edge info: "body" is missing in the request')
            response["body"] = 'Must include "body" in the request'
            response["status"] = 400
            return response

        velocloud_host: str = request_body.get("host", missing)
        if velocloud_host is missing:
            self._logger.error(f'Cannot get links with edge info: "host" is missing in the body of the request')
            response["body"] = 'Must include "host" in the body of the request'
            response["status"] = 400
            return response

        self._logger.info(f'Getting links with edge info from Velocloud host "{velocloud_host}"...')
        links_with_edge_info_response: dict = await self._velocloud_repository.get_links_with_edge_info(velocloud_host)

        response = {
            "request_id": request_id,
            **links_with_edge_info_response,
        }
        return response

    async def enterprise_edge_list(self, msg):
        self._logger.info("Getting enterprise edge list")
        enterprise_edge_list_response = {"request_id": msg["request_id"], "body": None, "status": None}

        if msg.get("body") is None:
            enterprise_edge_list_response["status"] = 400
            enterprise_edge_list_response["body"] = 'Must include "body" in request'
            return enterprise_edge_list_response

        if not all(key in msg["body"].keys() for key in ("host", "enterprise_id")):
            enterprise_edge_list_response["status"] = 400
            enterprise_edge_list_response["body"] = 'Must include "host" and "enterprise_id" in request "body"'
            return enterprise_edge_list_response

        host = msg["body"]["host"]
        enterprise_id = msg["body"]["enterprise_id"]

        enterprise_edge_list = await self._velocloud_repository.get_enterprise_edges(host, enterprise_id)

        enterprise_edge_list_response["body"] = enterprise_edge_list["body"]
        enterprise_edge_list_response["status"] = enterprise_edge_list["status"]

        return enterprise_edge_list_response

    async def links_configuration(self, msg: dict):
        edge_config_module_request = {"request_id": msg["request_id"], "body": None, "status": None}

        if msg.get("body") is None:
            edge_config_module_request["status"] = 400
            edge_config_module_request["body"] = 'Must include "body" in request'
            return edge_config_module_request

        if not all(key in msg["body"].keys() for key in ("host", "enterprise_id", "edge_id")):
            edge_config_module_request["status"] = 400
            edge_config_module_request["body"] = (
                "You must specify " '{..."body": {"host", "enterprise_id", "edge_id"}...} in the request'
            )
        else:
            edge_full_id = msg["body"]
            config_response = await self._velocloud_repository.get_links_configuration(edge_full_id)
            edge_config_module_request["status"] = config_response["status"]
            edge_config_module_request["body"] = config_response["body"]

        return edge_config_module_request
