import json


class GetAffectingTicketDetailsByEdgeSerial:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_affecting_ticket_details_by_edge_serial(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'ticket_details_list': None,
            'status': None
        }
        if msg.get("edge_serial") and msg.get("client_id"):

            edge_serial = msg['edge_serial']
            client_id = msg['client_id']

            self._logger.info(
                f'Looking for an affecting ticket for edge with serial {edge_serial} '
                f'(client ID: {client_id})...'
            )

            ticket_details_list = self._bruin_repository.get_affecting_ticket_details_by_edge_serial(
                edge_serial=edge_serial, client_id=client_id,
            )

            response["ticket_details_list"] = ticket_details_list["body"]
            response["status"] = ticket_details_list["status_code"]

            self._logger.info(
                f'Publishing response to affecting ticket details request for edge with serial {edge_serial} '
                f'(client ID: {client_id}) in {msg["response_topic"]} topic'
            )

        else:
            self._logger.error(f'Cannot get affecting ticket details using {json.dumps(msg)}. '
                               f'JSON malformed')

            response["ticket_details_list"] = 'You must specify "client_id", "edge_serial", in the request'
            response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], response)
