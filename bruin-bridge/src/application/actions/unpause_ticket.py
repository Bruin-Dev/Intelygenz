import json


class UnpauseTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def unpause_ticket(self, msg: dict):
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
        serial_number = body.get("serial_number")
        detail_id = body.get("detail_id")

        if not ticket_id or (not serial_number and not detail_id):
            self._logger.error(f'Cannot unpause a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["body"] = 'You must include ticket_id and serial_number or detail_id in the request'
            response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        self._logger.info(
            f'Unpause the ticket for ticket id: {ticket_id}, '
            f'serial number: {serial_number} and detail id: {detail_id}')
        result = await self._bruin_repository.unpause_ticket(ticket_id, serial_number, detail_id)

        response['body'] = result['body']
        response["status"] = result["status"]

        self._logger.info(
            f'Response from unpause: {response} to the ticket with ticket id: {ticket_id}, '
            f'serial number: {serial_number} and detail id {detail_id}')

        await self._event_bus.publish_message(msg['response_topic'], response)
