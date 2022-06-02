import json


class PostMultipleNotes:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_multiple_notes(self, msg: dict):
        response = {"request_id": msg["request_id"], "body": None, "status": None}

        body = msg.get("body")
        if body is None:
            self._logger.error(f"Cannot post a note to ticket using {json.dumps(msg)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if not all(key in body.keys() for key in ("ticket_id", "notes")):
            response["body"] = 'You must include "ticket_id" and "notes" in the body of the request'
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        ticket_id = body["ticket_id"]
        notes = body["notes"]

        for note in notes:
            if "text" not in note.keys() or not any(key in note.keys() for key in ("service_number", "detail_id")):
                response["body"] = (
                    'You must include "text" and any of "service_number" and "detail_id" for every '
                    'note in the "notes" field'
                )
                response["status"] = 400
                await self._event_bus.publish_message(msg["response_topic"], response)
                return

        self._logger.info(f"Posting multiple notes for ticket {ticket_id}...")
        result = await self._bruin_repository.post_multiple_ticket_notes(ticket_id, notes)

        response["body"] = result["body"]
        response["status"] = result["status"]

        await self._event_bus.publish_message(msg["response_topic"], response)
