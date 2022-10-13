import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class GetTicket:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        filtered_tickets_response = {"body": None, "status": None}
        body = payload.get("body")

        if body is None:
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(filtered_tickets_response))
            return

        if not all(key in body.keys() for key in ("client_id", "ticket_topic", "ticket_status")):
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = (
                "You must specify "
                '{..."body:{"client_id", "ticket_topic",'
                ' "ticket_status":[list of statuses]}...} in the request'
            )
            await msg.respond(to_json_bytes(filtered_tickets_response))
            return

        ticket_status = body["ticket_status"]

        params = {"client_id": body["client_id"], "ticket_topic": body["ticket_topic"]}

        category = body.get("category")
        if category:
            params["product_category"] = category

        ticket_id = body.get("ticket_id")
        if ticket_id:
            params["ticket_id"] = ticket_id

        service_number = body.get("service_number")
        if service_number:
            params["service_number"] = service_number

        # Valid date format: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date

        logger.info(f'Collecting all tickets for client id: {params["client_id"]}...')

        filtered_tickets = await self._bruin_repository.get_all_filtered_tickets(params, ticket_status)

        filtered_tickets_response = {**filtered_tickets_response, **filtered_tickets}

        logger.info(f'All tickets for client id: {params["client_id"]} sent')

        await msg.respond(to_json_bytes(filtered_tickets_response))
