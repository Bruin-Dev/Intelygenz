import json


class GetTicketDetail:

    def __init__(self, logger, event_bus, bruin_client):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_client = bruin_client

    async def send_ticket_detail(self, msg):
        msg_dict = json.loads(msg)
        ticket_id = msg_dict["ticket_id"]
        self._logger(f'Collecting ticket details for ticket id: {ticket_id}...')
        status = 500
        ticket_details = self._bruin_client.get_ticket_details(ticket_id)
        if ticket_details is not None:
            status = 200

        response = {
            'request_id': msg_dict['request_id'],
            'ticket_details': ticket_details,
            'status': status
        }

        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
        self._logger(f'Ticket details for ticket id: {ticket_id} sent!')
