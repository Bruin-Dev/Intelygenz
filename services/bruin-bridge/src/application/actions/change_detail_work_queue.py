import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class ChangeDetailWorkQueue:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        msg_body = payload.get("body")
        if not msg_body:
            logger.error(f"Cannot change detail work queue using {json.dumps(payload)}. JSON malformed")
            response["body"] = (
                'You must specify {.."body": {"service_number", "ticket_id", "detail_id", "queue_name"}..} '
                "in the request"
            )
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in msg_body.keys() for key in ("ticket_id", "queue_name")) or not any(
            key in msg_body.keys() for key in ("service_number", "detail_id")
        ):
            logger.error(
                f"Cannot change detail work queue using {json.dumps(msg_body)}. "
                f'Need all these parameters: "service_number" or "detail_id", "ticket_id", "queue_name"'
            )
            response["body"] = (
                'You must specify {.."body": {"service_number" or "detail_id", "ticket_id", "queue_name"}..} '
                "in the request"
            )
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = msg_body.pop("ticket_id")
        logger.info(f"Changing work queue of ticket {ticket_id} with filters: {json.dumps(msg_body)}")

        result = await self._bruin_repository.change_detail_work_queue(ticket_id, filters=msg_body)

        response["body"] = result["body"]
        response["status"] = result["status"]
        await msg.respond(to_json_bytes(response))

        logger.info(
            f"Result of changing work queue of ticket {ticket_id} with filters {json.dumps(msg_body)} "
            "published in event bus!"
        )
