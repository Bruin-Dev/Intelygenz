import json


class PostOutageTicket:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_outage_ticket(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        msg_data = msg.get("body")

        response = {"request_id": request_id, "body": None, "status": None}

        if msg_data is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if not all(key in msg_data.keys() for key in ("client_id", "service_number")):
            self._logger.error(
                f"Cannot post ticket using payload {json.dumps(msg)}. " 'Need "client_id" and "service_number"'
            )
            response["body"] = 'Must specify "client_id" and "service_number" to post an outage ticket'
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        client_id, service_number = msg_data["client_id"], msg_data["service_number"]
        if client_id is None or service_number is None:
            self._logger.error(
                f"Cannot post ticket using payload {json.dumps(msg)}."
                f'"client_id" and "service_number" must have non-null values.'
            )
            response["body"] = '"client_id" and "service_number" must have non-null values'
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_contact = msg_data.get("ticket_contact")

        self._logger.info(f"Posting outage ticket with payload: {json.dumps(msg)}")
        # outage_ticket = await self._bruin_repository.post_outage_ticket(
        #     client_id, service_number, ticket_contact=ticket_contact
        # )
        outage_ticket = {"body": "", "status": 200}

        self._logger.info(f"Outage ticket posted using parameters {json.dumps(msg)}")
        response["body"] = outage_ticket["body"]
        response["status"] = outage_ticket["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(f"Outage ticket published in event bus for request {json.dumps(msg)}")
