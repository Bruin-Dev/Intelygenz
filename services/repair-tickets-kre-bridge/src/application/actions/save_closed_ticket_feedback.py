import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class SaveClosedTicketFeedback:
    def __init__(self, repository):
        self._kre_repository = repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {
            "request_id": request_id,
            "body": "",
            "status": 0,
        }

        payload = payload.get("body")
        ticket_id = payload.get("ticket_id")
        if not payload or not ticket_id:
            logger.error(f"Error cannot save feedback for ticket: {ticket_id}. error JSON malformed")
            response["body"] = "You must use correct format in the request"
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        save_closed_tickets_response = await self._kre_repository.save_closed_ticket_feedback(payload)
        response["body"] = save_closed_tickets_response["body"]
        response["status"] = save_closed_tickets_response["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(f"Save closed tickets result for ticket {ticket_id} published in event bus!")
