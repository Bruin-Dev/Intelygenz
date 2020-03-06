import json


class GetOutageTicketDetailsByEdgeSerial:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def send_outage_ticket_details_by_edge_serial(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        body = msg.get("body")
        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        edge_serial = body.get("edge_serial")
        client_id = body.get('client_id')
        if not edge_serial or not client_id:
            self._logger.error(f'Cannot get outage ticket details using {json.dumps(msg)}. JSON malformed')
            response["body"] = 'You must specify "client_id", "edge_serial", in the request'
            response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        ticket_statuses = body.get('ticket_statuses')

        self._logger.info(
            f'Looking for an outage ticket for edge with serial {edge_serial} '
            f'(client ID: {client_id})...'
        )

        ticket_details_list = self._bruin_repository.get_outage_ticket_details_by_edge_serial(
            edge_serial=edge_serial, client_id=client_id, ticket_statuses=ticket_statuses,
        )

        response["body"] = ticket_details_list["body"]
        response["status"] = ticket_details_list["status"]

        self._logger.info(
            f'Publishing response to outage ticket details request for edge with serial {edge_serial} '
            f'(client ID: {client_id}) in {msg["response_topic"]} topic'
        )

        await self._event_bus.publish_message(msg['response_topic'], response)
