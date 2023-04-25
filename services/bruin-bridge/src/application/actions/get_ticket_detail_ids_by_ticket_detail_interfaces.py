import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetDetailIdsByTicketDetailInterfaces:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        detail_response = {"body": None, "status": None}
        if payload.get("body") is None:
            detail_response["status"] = 400
            detail_response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(detail_response))
            return

        ticket_id = payload["body"].get("ticket_id")
        detail_id = payload["body"].get("detail_id")
        interfaces = payload["body"].get("interfaces")
        if ticket_id is None or detail_id is None or interfaces is None:
            logger.error(f"Cannot get ticket_details using {json.dumps(payload)}. JSON malformed")

            detail_response["body"] = "You must include ticket_id, detail_id and interfaces in the request"
            detail_response["status"] = 400
            await msg.respond(to_json_bytes(detail_response))
            return

        logger.info(
            f"Collecting ticket detailIds for ticket id: {ticket_id}, "
            f"detail id: {detail_id}, interfaces: {interfaces}...")
        ticket_details = await self._bruin_repository.get_ticket_detail_ids_by_ticket_detail_interfaces(
            ticket_id, detail_id, interfaces)

        detail_response["body"] = ticket_details["body"]
        detail_response["status"] = ticket_details["status"]
        logger.info(f"Ticket detailIds for ticket id: {ticket_id}, "
                    f"detail id: {detail_id}, interfaces: {interfaces} sent!")

        await msg.respond(to_json_bytes(detail_response))
