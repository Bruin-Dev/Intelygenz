import json


class OpenTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def open_ticket(self, msg: dict):
        ticket_id = msg["ticket_id"]
        detail_id = msg["detail_id"]

        self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to OPEN')
        status = 500
        result = self._bruin_repository.open_ticket(ticket_id, detail_id)
        if result is not None:
            self._logger.info(f'Status: OPEN')
            status = 200
        response = {
            'request_id': msg['request_id'],
            'status': status
        }
        await self._event_bus.publish_message(msg['response_topic'], response)
