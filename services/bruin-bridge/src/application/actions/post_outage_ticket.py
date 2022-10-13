import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class PostOutageTicket:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        msg_data = payload.get("body")

        response = {"body": None, "status": None}

        if msg_data is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in msg_data.keys() for key in ("client_id", "service_number")):
            logger.error(
                f"Cannot post ticket using payload {json.dumps(payload)}. " 'Need "client_id" and "service_number"'
            )
            response["body"] = 'Must specify "client_id" and "service_number" to post an outage ticket'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        client_id, service_number = msg_data["client_id"], msg_data["service_number"]
        if client_id is None or service_number is None:
            logger.error(
                f"Cannot post ticket using payload {json.dumps(payload)}."
                f'"client_id" and "service_number" must have non-null values.'
            )
            response["body"] = '"client_id" and "service_number" must have non-null values'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_contact = msg_data.get("ticket_contact")

        logger.info(f"Posting outage ticket with payload: {json.dumps(payload)}")
        outage_ticket = await self._bruin_repository.post_outage_ticket(
            client_id, service_number, ticket_contact=ticket_contact
        )

        logger.info(f"Outage ticket posted using parameters {json.dumps(payload)}")
        response["body"] = outage_ticket["body"]
        response["status"] = outage_ticket["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(f"Outage ticket published in event bus for request {json.dumps(payload)}")
