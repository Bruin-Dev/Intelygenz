import requests
import json


class BruinTicketResponse:

    def __init__(self, logger, config, event_bus, bruin_client):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_client = bruin_client

    async def report_all_bruin_tickets(self, msg):
        msg_dict = json.loads(msg)
        self._logger.info(f'Collecting all tickets for client id: { msg_dict["client_id"]}...')
        ticket_id = ''
        if 'ticket_id' in msg_dict.keys():
            ticket_id = msg_dict['ticket_id']
        client_id = msg_dict['client_id']
        status = 500
        filtered_tickets = self._bruin_client.get_all_filtered_tickets(client_id, ticket_id)
        if filtered_tickets is not None:
            status = 200

        filtered_tickets_response = {
                                     'request_id': msg_dict['request_id'],
                                     'tickets': filtered_tickets,
                                     'status': status
                                    }

        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(filtered_tickets_response, default=str))

        self._logger.info(f'All tickets for client id: {client_id} sent')
