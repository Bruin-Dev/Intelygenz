import json
import logging

import humps
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class DiGiRecoveryLogs:
    def __init__(self, digi_repository):
        self._digi_repository = digi_repository

    async def __call__(self, request_msg: Msg):

        msg_data = json.loads(request_msg.data)
        response = {"request_id": msg_data["request_id"], "body": None, "status": None}
        request_filters = msg_data.get("body")

        if not request_filters:
            logger.error(f"Cannot reboot DiGi client using {request_msg}. JSON malformed")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'

        else:
            digi_recovery_logs_response = await self._digi_repository.get_digi_recovery_logs(
                humps.pascalize(request_filters)
            )

            response["body"] = digi_recovery_logs_response["body"]
            response["status"] = digi_recovery_logs_response["status"]

        await request_msg.respond(json.dumps(response).encode())
        logger.info(
            f"DiGi recovery logs retrieved and publishing results in event bus for request {request_msg}. "
            f"Message published was {response}"
        )
