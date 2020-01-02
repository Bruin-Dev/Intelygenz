class GetOutageTicketDetailsByEdgeSerial:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_outage_ticket_details_by_edge_serial(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        edge_serial = msg['edge_serial']
        client_id = msg['client_id']

        self._logger.info(
            f'Looking for an outage ticket for edge with serial {edge_serial} '
            f'(client ID: {client_id})...'
        )

        ticket_details = self._bruin_repository.get_outage_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
        )
        if ticket_details:
            status = 200
            self._logger.info(
                f'Ticket found for edge with serial {edge_serial} and client ID {client_id}. '
                f'Ticket ID is {ticket_details["ticketID"]}.')
        else:
            status = 500
            self._logger.info(
                f'Error trying to get a ticket for edge with serial {edge_serial} and client ID {client_id}.')

        response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': status
        }
        await self._event_bus.publish_message(response_topic, response)

        self._logger.info(
            f'Publishing response to outage ticket details request for edge with serial {edge_serial} '
            f'(client ID: {client_id}) in {response_topic} topic'
        )
