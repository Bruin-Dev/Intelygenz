class EnterpriseEdgeList:
    def __init__(self, event_bus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def enterprise_edge_list(self, msg):
        self._logger.info("Getting enterprise edge list")
        enterprise_edge_list_response = {
            "request_id": msg['request_id'],
            "body": None,
            "status": None
        }

        if msg.get("body") is None:
            enterprise_edge_list_response["status"] = 400
            enterprise_edge_list_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], enterprise_edge_list_response)
            return

        if not all(key in msg['body'].keys() for key in ("host", "enterprise_id")):
            enterprise_edge_list_response["status"] = 400
            enterprise_edge_list_response["body"] = 'Must include "host" and "enterprise_id" in request "body"'
            await self._event_bus.publish_message(msg['response_topic'], enterprise_edge_list_response)
            return

        host = msg["body"]["host"]
        enterprise_id = msg["body"]["enterprise_id"]

        enterprise_edge_list = await self._velocloud_repository.get_enterprise_edges(host, enterprise_id)

        enterprise_edge_list_response["body"] = enterprise_edge_list["body"]
        enterprise_edge_list_response["status"] = enterprise_edge_list["status"]

        await self._event_bus.publish_message(msg['response_topic'], enterprise_edge_list_response)
        self._logger.info(f"Sent list of enterprise edges for enterprise {enterprise_id} and host {host}")
