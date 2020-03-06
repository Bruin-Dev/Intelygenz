import json


class OpenTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def open_ticket(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        ticket_id = body.get("ticket_id")
        detail_id = body.get("detail_id")

        if not ticket_id or not detail_id:
            self._logger.error(f'Cannot open a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["body"] = 'You must include ticket_id and detail_id in the request'
            response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to OPEN')
        result = self._bruin_repository.open_ticket(ticket_id, detail_id)

        response['body'] = result['body']
        response["status"] = result["status"]

        await self._event_bus.publish_message(msg['response_topic'], response)
