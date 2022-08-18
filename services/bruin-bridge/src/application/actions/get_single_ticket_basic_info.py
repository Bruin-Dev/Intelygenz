import json

missing = object()


class GetSingleTicketBasicInfo:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_single_ticket_basic_info(self, msg: dict):
        request_id = msg["request_id"]
        response_msg = {"request_id": request_id, "body": None, "status": None}

        bruin_payload: dict = msg.get("body", missing)
        if bruin_payload is missing:
            self._logger.error(f"Cannot get tickets basic info using {json.dumps(msg)}. JSON malformed")
            response_msg["body"] = 'Must include "body" in the request message'
            response_msg["status"] = 400

            await self._event_bus.publish_message(msg["response_topic"], response_msg)
            return

        ticket_id: int = bruin_payload.pop("ticket_id", missing)

        if ticket_id is missing:
            self._logger.error(
                f"Cannot get tickets basic info using {json.dumps(msg)}. Need a TicketId to keep going."
            )
            response_msg["body"] = f'Must specify "ticket_id" in the body of the request'
            response_msg["status"] = 400

            await self._event_bus.publish_message(msg["response_topic"], response_msg)
            return

        self._logger.info(f"Fetching basic info for ticket {ticket_id}")

        tickets_basic_info: dict = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)

        response_msg["body"] = tickets_basic_info["body"]
        response_msg["status"] = tickets_basic_info["status"]

        self._logger.info(f"Publishing ticket data to the event bus...")
        await self._event_bus.publish_message(msg["response_topic"], response_msg)
