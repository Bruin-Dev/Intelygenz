import json


class GetOutageTicketDetailsByEdgeSerial:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_outage_ticket_details_by_edge_serial(self, msg: dict):
        response_topic = msg['response_topic']

        response = {
            'request_id': msg['request_id'],
            'ticket_details': None,
            'status': None
        }

        if "edge_serial" not in msg.keys() or "client_id" not in msg.keys():
            self._logger.error(f'Cannot get outage ticket details using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must specify ' \
                                        '"client_id", "edge_serial", in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        edge_serial = msg['edge_serial']
        client_id = msg['client_id']
        ticket_statuses = msg.get('ticket_statuses')

        self._logger.info(
            f'Looking for an outage ticket for edge with serial {edge_serial} '
            f'(client ID: {client_id})...'
        )

        ticket_details_list = self._bruin_repository.get_outage_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id, ticket_statuses=ticket_statuses,
        )

        if ticket_details_list["status_code"] in range(200, 300):
            response['ticket_details'] = ticket_details_list["body"]
            response["status"] = 200
            self._logger.info(f'Ticket details found from serial:{edge_serial}')
        elif ticket_details_list["status_code"] == 400:
            response["status"] = 400
            response["error_message"] = f"Bad request when retrieving ticket details: {ticket_details_list['body']}"
            self._logger.error(f'Error trying to get ticket details from serial:{edge_serial}')
        elif ticket_details_list["status_code"] == 401:
            response["status"] = 400
            response["error_message"] = f"Authentication error in bruin API."
            self._logger.error(f'Error trying to authenticate against bruin API: {ticket_details_list["body"]}')
        elif ticket_details_list["status_code"] in range(500, 513):
            response["status"] = 500
            response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accessing bruin API: {ticket_details_list["body"]}')
        await self._event_bus.publish_message(response_topic, response)

        self._logger.info(
            f'Publishing response to outage ticket details request for edge with serial {edge_serial} '
            f'(client ID: {client_id}) in {response_topic} topic'
        )
