import json


class GetTicketDetails:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_ticket_details(self, msg: dict):
        detail_response = {
            'request_id': msg['request_id'],
            'ticket_details': None,
            'status': None
        }

        if msg.get("ticket_id"):
            ticket_id = msg["ticket_id"]

            self._logger.info(f'Collecting ticket details for ticket id: {ticket_id}...')
            ticket_details = self._bruin_repository.get_ticket_details(ticket_id)

            detail_response['ticket_details'] = ticket_details['body']
            detail_response['status'] = ticket_details['status_code']
            self._logger.info(f'Ticket details for ticket id: {ticket_id} sent!')
        else:
            self._logger.error(f'Cannot get ticket_details using {json.dumps(msg)}. '
                               f'JSON malformed')

            detail_response["ticket_details"] = 'You must include ticket_id in the request'
            detail_response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], detail_response)
