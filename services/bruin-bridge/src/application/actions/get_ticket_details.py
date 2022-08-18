import json


class GetTicketDetails:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_ticket_details(self, msg: dict):
        detail_response = {"request_id": msg["request_id"], "body": None, "status": None}
        if msg.get("body") is None:
            detail_response["status"] = 400
            detail_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], detail_response)
            return
        ticket_id = msg["body"].get("ticket_id")
        if ticket_id is None:
            self._logger.error(f"Cannot get ticket_details using {json.dumps(msg)}. JSON malformed")

            detail_response["body"] = "You must include ticket_id in the request"
            detail_response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], detail_response)
            return

        self._logger.info(f"Collecting ticket details for ticket id: {ticket_id}...")
        ticket_details = await self._bruin_repository.get_ticket_details(ticket_id)

        detail_response["body"] = ticket_details["body"]
        detail_response["status"] = ticket_details["status"]
        self._logger.info(f"Ticket details for ticket id: {ticket_id} sent!")

        await self._event_bus.publish_message(msg["response_topic"], detail_response)
