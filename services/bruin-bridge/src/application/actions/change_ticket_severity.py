import json

missing = object()


class ChangeTicketSeverity:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def change_ticket_severity(self, msg: dict):
        request_id = msg["request_id"]
        response_msg = {"request_id": request_id, "body": None, "status": None}

        payload: dict = msg.get("body", missing)
        if payload is missing:
            self._logger.error(f"Cannot change ticket severity level using {json.dumps(msg)}. JSON malformed")
            response_msg["body"] = 'Must include "body" in the request message'
            response_msg["status"] = 400

            await self._event_bus.publish_message(msg["response_topic"], response_msg)
            return

        if not all(key in payload.keys() for key in ("ticket_id", "severity", "reason")):
            self._logger.error(
                f"Cannot change ticket severity level using {json.dumps(msg)}. "
                'Need fields "ticket_id", "severity" and "reason".'
            )
            response_msg["body"] = f'You must specify "ticket_id", "severity" and "reason" in the body'
            response_msg["status"] = 400

            await self._event_bus.publish_message(msg["response_topic"], response_msg)
            return

        self._logger.info(f"Changing ticket severity level using parameters {json.dumps(payload)}...")
        ticket_id = payload.pop("ticket_id")
        change_ticket_severity_response: dict = await self._bruin_repository.change_ticket_severity(ticket_id, payload)

        response_msg["body"] = change_ticket_severity_response["body"]
        response_msg["status"] = change_ticket_severity_response["status"]

        self._logger.info(
            f"Publishing result of changing severity level of ticket {ticket_id} using payload {json.dumps(payload)} "
            "to the event bus..."
        )
        await self._event_bus.publish_message(msg["response_topic"], response_msg)
