import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class ChangeTicketSeverity:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response_msg = {"body": None, "status": None}

        body: dict = payload.get("body")
        if body is None:
            logger.error(f"Cannot change ticket severity level using {json.dumps(body)}. JSON malformed")
            response_msg["body"] = 'Must include "body" in the request message'
            response_msg["status"] = 400

            await msg.respond(to_json_bytes(response_msg))
            return

        if not all(key in body.keys() for key in ("ticket_id", "severity", "reason")):
            logger.error(
                f"Cannot change ticket severity level using {json.dumps(body)}. "
                'Need fields "ticket_id", "severity" and "reason".'
            )
            response_msg["body"] = f'You must specify "ticket_id", "severity" and "reason" in the body'
            response_msg["status"] = 400

            await msg.respond(to_json_bytes(response_msg))
            return

        logger.info(f"Changing ticket severity level using parameters {json.dumps(body)}...")
        ticket_id = body.pop("ticket_id")
        change_ticket_severity_response: dict = await self._bruin_repository.change_ticket_severity(ticket_id, body)

        response_msg["body"] = change_ticket_severity_response["body"]
        response_msg["status"] = change_ticket_severity_response["status"]

        logger.info(
            f"Publishing result of changing severity level of ticket {ticket_id} using payload {json.dumps(body)} "
            "to the event bus..."
        )
        await msg.respond(to_json_bytes(response_msg))
