import json
import logging

from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetProbes:
    def __init__(self, hawkeye_repository):
        self._hawkeye_repository = hawkeye_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)
        probes_response = {"request_id": payload["request_id"], "body": None, "status": None}
        filters = {}
        body = payload.get("body")

        if body is None:
            logger.error(f"Cannot get probes using {json.dumps(payload)}. JSON malformed")
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "body" in request'
            await msg.respond(data=json.dumps(probes_response).encode())
            return

        if "serial_number" in body:
            filters["serial_number"] = body["serial_number"]
        if "status" in body:
            filters["status"] = body["status"]

        logger.info(f"Collecting all probes with filters: {json.dumps(filters)}...")

        filtered_probes = await self._hawkeye_repository.get_probes(filters)

        filtered_probes_response = {**probes_response, **filtered_probes}

        await msg.respond(data=json.dumps(filtered_probes_response).encode())
