import json


class GetTicketDetailsByEdgeSerial:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_ticket_details_by_edge_serial(self, msg):
        msg_dict = json.loads(msg)
        request_id = msg_dict['request_id']
        response_topic = msg_dict['response_topic']
        edge_serial = msg_dict["edge_serial"]
        client_id = msg_dict["client_id"]

        self._logger.info(
            f'Looking for a ticket for edge with serial {edge_serial} '
            f'(client ID: {client_id})...'
        )

        ticket_details = self._bruin_repository.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id,
        )
        ticket_id = ticket_details['ticketID']
        if ticket_id:
            status = 200
            self._logger.info(
                f'Ticket found for edge with serial {edge_serial} and client ID {client_id}. '
                f'Ticket ID is {ticket_id}.')
        else:
            status = 500
            self._logger.info(
                f'Ticket not found for edge with serial {edge_serial} and client ID {client_id}.')

        response = {
            'request_id': request_id,
            'ticket_details': ticket_details,
            'status': status
        }
        await self._event_bus.publish_message(response_topic, json.dumps(response))

        self._logger.info(f'Details of ticket {ticket_id} published in {response_topic} topic!')
