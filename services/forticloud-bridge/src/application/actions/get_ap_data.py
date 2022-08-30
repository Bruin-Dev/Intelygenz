import json
import logging

from nats.aio.msg import Msg

from ..repositories.forticloud_repository import ForticloudRepository

logger = logging.getLogger(__name__)

PAYLOAD_MODEL = {
    "fields": ["name", "admin", "_conn-state"],
    "target": ["adom/production/group/All_FortiGate"],
}

REQUEST_MODEL = {
    "response_topic": "some_temp_topic",
    "body": {"payload": PAYLOAD_MODEL},
}


class GetApData:
    def __init__(self, forticloud_repository: ForticloudRepository):
        self._forticloud_repository = forticloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            logger.error(f"Cannot get AP data with {json.dumps(payload)}. JSON malformed")

            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in REQUEST_MODEL["body"].keys()):
            logger.error(
                f"Cannot get AP data with {json.dumps(payload)}. Make sure it complies with the shape of "
                f"{REQUEST_MODEL}"
            )

            response["status"] = 400
            response["body"] = f"Request's should look like {REQUEST_MODEL}"
            await msg.respond(json.dumps(response).encode())
            return

        payload = payload["body"]["payload"]

        logger.info(f"Getting AP data for payload {payload}...")
        response = await self._forticloud_repository.get_ap_data(payload=payload)
        response["status"] = response["status"]
        response["body"] = response["body"]

        await msg.respond(json.dumps(response).encode())
        logger.info(f"Published AP data for payload {payload}")
