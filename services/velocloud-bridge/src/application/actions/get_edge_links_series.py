PAYLOAD_MODEL = {
    "enterpriseId": 0,
    "edgeId": 0,
    "interval": {"start": 19191919, "end": 19191999},
    "metrics": ["bytesTx", "bytesRx"],
}

REQUEST_MODEL = {
    "request_id": "19aafcjh10199",
    "response_topic": "some_temp_topic",
    "body": {"host": "mettel.velocloud.net", "payload": PAYLOAD_MODEL},
}


class GetEdgeLinksSeries:
    # "data" array of a series has a limit of 1024 items, therefore the max interval is 3 days
    # If the time difference is lesser than 15 min between start and end it will return an empty array response

    def __init__(self, event_bus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def edge_links_series(self, msg: dict):
        edge_links_series_response = {"request_id": msg["request_id"], "body": None, "status": None}

        if msg.get("body") is None:
            edge_links_series_response["status"] = 400
            edge_links_series_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], edge_links_series_response)
            return

        if not all(key in msg["body"].keys() for key in REQUEST_MODEL["body"].keys()):
            edge_links_series_response["status"] = 400
            edge_links_series_response["body"] = f"Request's should look like {REQUEST_MODEL}"
            if not all(key in msg["body"]["payload"].keys() for key in PAYLOAD_MODEL.keys()):
                edge_links_series_response["status"] = 400
                edge_links_series_response["body"] = f"Request's payload should look like {PAYLOAD_MODEL}"
        else:
            host = msg["body"]["host"]
            payload = msg["body"]["payload"]
            response = await self._velocloud_repository.get_edge_links_series(host, payload)
            edge_links_series_response["status"] = response["status"]
            edge_links_series_response["body"] = response["body"]

        await self._event_bus.publish_message(msg["response_topic"], edge_links_series_response)
