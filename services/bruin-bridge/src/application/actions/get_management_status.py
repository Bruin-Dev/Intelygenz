import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetManagementStatus:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        filters = payload.get("body")
        if "body" not in payload.keys():
            logger.error(f"Cannot get management status using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = (
                "You must specify " '{.."body":{"client_id", "status", "service_number"}...} in the request'
            )
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in filters.keys() for key in ("client_id", "status", "service_number")):
            logger.info(
                f"Cannot get management status using {json.dumps(filters)}. "
                f'Need "client_id", "status", "service_number"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "client_id", "status", "service_number" in the filter'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting management status with filters: {json.dumps(filters)}")

        management_status = await self._bruin_repository.get_management_status(filters)

        response["body"] = management_status["body"]
        response["status"] = management_status["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"Management status published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
