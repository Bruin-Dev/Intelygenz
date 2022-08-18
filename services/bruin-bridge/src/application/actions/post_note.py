import json


class PostNote:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_note(self, msg: dict):
        response = {"request_id": msg["request_id"], "body": None, "status": None}
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if not all(key in body.keys() for key in ("ticket_id", "note")):
            self._logger.error(f"Cannot post a note to ticket using {json.dumps(msg)}. JSON malformed")

            response["body"] = 'You must include "ticket_id" and "note" in the "body" field of the response request'
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        ticket_id = msg["body"]["ticket_id"]
        note = msg["body"]["note"]

        self._logger.info(f"Putting note in: {ticket_id}...")

        service_numbers: list = msg["body"].get("service_numbers")
        result = await self._bruin_repository.post_ticket_note(ticket_id, note, service_numbers=service_numbers)

        response["body"] = result["body"]
        response["status"] = result["status"]
        self._logger.info(f"Note successfully posted to ticketID:{ticket_id} ")

        await self._event_bus.publish_message(msg["response_topic"], response)
