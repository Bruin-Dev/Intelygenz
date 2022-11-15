import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetNextResultsForTicketDetail:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        request_body = payload.get("body")
        if not request_body:
            logger.error(f"Cannot get next results for ticket detail using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response[
                "body"
            ] = 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request'
            await msg.respond(to_json_bytes(response))
            return

        if list(request_body.keys()) != ["ticket_id", "detail_id", "service_number"]:
            logger.info(
                f"Cannot get next results for ticket detail using {json.dumps(request_body)}. "
                f'Need "ticket_id", "detail_id", "service_number"'
            )
            response["status"] = 400
            response[
                "body"
            ] = 'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request'
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = request_body["ticket_id"]
        detail_id = request_body["detail_id"]
        service_number = request_body["service_number"]

        logger.info(f"Claiming all available next results for ticket {ticket_id} and detail {detail_id}...")
        next_results = await self._bruin_repository.get_next_results_for_ticket_detail(
            ticket_id, detail_id, service_number
        )
        logger.info(f"Got all available next results for ticket {ticket_id} and detail {detail_id}!")

        response["body"] = next_results["body"]
        response["status"] = next_results["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(f"Next results for ticket {ticket_id} and detail {detail_id} published in event bus!")
