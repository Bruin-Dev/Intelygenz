import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)

PAYLOAD_MODEL = {
    "enterpriseId": 0,
    "edgeId": 0,
    "interval": {"start": 19191919, "end": 19191999},
    "metrics": ["bytesTx", "bytesRx"],
}

REQUEST_MODEL = {
    "response_topic": "some_temp_topic",
    "body": {"host": "mettel.velocloud.net", "payload": PAYLOAD_MODEL},
}


class GetEdgeLinksSeries:
    # "data" array of a series has a limit of 1024 items, therefore the max interval is 3 days
    # If the time difference is lesser than 15 min between start and end it will return an empty array response

    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in REQUEST_MODEL["body"].keys()):
            response["status"] = 400
            response["body"] = f"Request's should look like {REQUEST_MODEL}"
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"]["payload"].keys() for key in PAYLOAD_MODEL.keys()):
            response["status"] = 400
            response["body"] = f"Request's payload should look like {PAYLOAD_MODEL}"
            await msg.respond(json.dumps(response).encode())
            return

        host = payload["body"]["host"]
        payload = payload["body"]["payload"]

        response = await self._velocloud_repository.get_edge_links_series(host=host, payload=payload)
        response["status"] = response["status"]
        response["body"] = response["body"]

        await msg.respond(json.dumps(response).encode())
