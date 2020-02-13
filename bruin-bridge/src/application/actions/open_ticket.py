import json


class OpenTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def open_ticket(self, msg: dict):
        response_topic = msg['response_topic']

        response = {
            'request_id': msg['request_id'],
            'status': None
        }

        if "ticket_id" not in msg.keys() or "detail_id" not in msg.keys():
            self._logger.error(f'Cannot open a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must include ticket_id and detail_id in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg["ticket_id"]
        detail_id = msg["detail_id"]

        self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to OPEN')
        result = self._bruin_repository.open_ticket(ticket_id, detail_id)

        if result["status_code"] in range(200, 300):
            response["status"] = 200
            self._logger.info(f'Ticket status for ticketID {ticket_id}: OPEN')
        elif result["status_code"] == 400:
            response["status"] = 400
            response["error_message"] = f"Bad request when opening ticket: {result['body']}"
            self._logger.error(f'Error trying to open ticket from ticketID:{ticket_id}')
        elif result["status_code"] == 401:
            response["status"] = 400
            response["error_message"] = f"Authentication error in bruin API."
            self._logger.error(f'Error trying to authenticate against bruin API: {result["body"]}')
        elif result["status_code"] in range(500, 513):
            response["status"] = 500
            response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accessing bruin API: {result["body"]}')

        await self._event_bus.publish_message(response_topic, response)
