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

        if msg.get("ticket_id") and msg.get("detail_id"):

            ticket_id = msg["ticket_id"]
            detail_id = msg["detail_id"]

            self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to OPEN')
            result = self._bruin_repository.open_ticket(ticket_id, detail_id)

            response['body'] = result['body']
            response["status"] = result["status"]
        else:
            self._logger.error(f'Cannot open a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["body"] = 'You must include ticket_id and detail_id in the request'
            response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], response)
