import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class GetTicketTaskHistory:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        if "body" not in payload.keys():
            logger.error(f"Cannot get ticket task history using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"ticket_id"}...} in the request'
            await msg.respond(to_json_bytes(response))
            return

        filters = payload["body"]

        if "ticket_id" not in filters.keys():
            logger.info(f"Cannot get get ticket task history using {json.dumps(filters)}. Need 'ticket_id'")
            response["status"] = 400
            response["body"] = 'You must specify "ticket_id" in the body'
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting ticket task history with filters: {json.dumps(filters)}")

        ticket_task_history = await self._bruin_repository.get_ticket_task_history(filters)

        response["body"] = ticket_task_history["body"]
        response["status"] = ticket_task_history["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"get ticket task history published in event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
