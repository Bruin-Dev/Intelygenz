class GetTicket:

    def __init__(self, logger, config, event_bus, bruin_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_all_tickets(self, msg: dict):
        self._logger.info(f'Collecting all tickets for client id: {msg["client_id"]}...')
        ticket_id = ''
        if 'ticket_id' in msg.keys():
            ticket_id = msg['ticket_id']
        client_id = msg['client_id']
        ticket_status = msg['ticket_status']
        category = msg['category']
        ticket_topic = msg['ticket_topic']
        status = 500
        filtered_tickets = self._bruin_repository.get_all_filtered_tickets(client_id,
                                                                           ticket_id,
                                                                           ticket_status,
                                                                           category,
                                                                           ticket_topic)
        if filtered_tickets is not None:
            status = 200

        filtered_tickets_response = {
                                     'request_id': msg['request_id'],
                                     'tickets': filtered_tickets,
                                     'status': status
                                    }

        await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)

        if filtered_tickets is not None:
            self._logger.info(f'Tickets that are going to be sent {len(filtered_tickets)}')

        self._logger.info(f'All tickets for client id: {client_id} sent')
