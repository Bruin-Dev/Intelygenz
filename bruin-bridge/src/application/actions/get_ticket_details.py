import json


class GetTicketDetails:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_ticket_details(self, msg: dict):
        response_topic = msg['response_topic']
        detail_response = {
            'request_id': msg['request_id'],
            'ticket_details': None,
            'status': None
        }

        if "ticket_id" not in msg.keys():
            self._logger.error(f'Cannot get ticket_details using {json.dumps(msg)}. '
                               f'JSON malformed')
            detail_response["status"] = 400
            detail_response["error_message"] = 'You must include ticket_id in the request'
            await self._event_bus.publish_message(response_topic, detail_response)
            return

        ticket_id = msg["ticket_id"]

        self._logger.info(f'Collecting ticket details for ticket id: {ticket_id}...')
        ticket_details = self._bruin_repository.get_ticket_details(ticket_id)

        if ticket_details["status_code"] in range(200, 300):
            detail_response['tickets'] = ticket_details["body"]
            detail_response["status"] = 200
            self._logger.info(f'Ticket details found from ticketID:{ticket_id}')
        elif ticket_details["status_code"] == 400:
            detail_response["status"] = 400
            detail_response["error_message"] = f"Bad request when retrieving ticket details: {ticket_details['body']}"
            self._logger.error(f'Error trying to get ticket details from ticketID:{ticket_id}')
        elif ticket_details["status_code"] == 401:
            detail_response["status"] = 400
            detail_response["error_message"] = f"Authentication error in bruin API."
            self._logger.error(f'Error trying to authenticate against bruin API: {ticket_details["body"]}')
        elif ticket_details["status_code"] in range(500, 513):
            detail_response["status"] = 500
            detail_response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accessing bruin API: {ticket_details["body"]}')

        await self._event_bus.publish_message(response_topic, detail_response)
        self._logger.info(f'Ticket details for ticket id: {ticket_id} sent!')
