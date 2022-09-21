import json
import logging

import humps
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class DiGiReboot:
    def __init__(self, digi_repository):
        self._digi_repository = digi_repository

    async def __call__(self, request_msg: Msg):

        msg_data = json.loads(request_msg.data)
        response = {"igzID": msg_data.get("igzID"), "body": None, "status": None}

        request_filters = msg_data.get("body")

        if not request_filters:
            logger.error(f"Cannot reboot DiGi client using {request_msg}. JSON malformed")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'

        elif not all(key in request_filters.keys() for key in ("velo_serial", "ticket", "MAC")):
            logger.error(f"Cannot reboot DiGi client using {request_msg}. JSON malformed")
            response["body"] = (
                'You must include "velo_serial", "ticket", "MAC" ' 'in the "body" field of the response request'
            )
            response["status"] = 400
        else:
            logger.info(f"Attempting to reboot DiGi client with payload of: {request_filters}")

            reboot_response = await self._digi_repository.reboot(humps.pascalize(request_filters))

            response["body"] = reboot_response["body"]
            response["status"] = reboot_response["status"]

        await request_msg.respond(json.dumps(response).encode())
        logger.info(
            f"DiGi reboot process completed and publishing results in event bus for request {request_msg}. "
            f"Message published was {response}"
        )
