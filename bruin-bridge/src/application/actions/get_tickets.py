import json


class GetTicket:

    def __init__(self, logger, config, event_bus, bruin_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_all_tickets(self, msg: dict):
        filtered_tickets_response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        if msg.get("body") is None:
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
            return
        body = msg['body']
        if all(key in body.keys() for key in ("client_id", "category", "ticket_topic", "ticket_status")):

            ticket_status = body['ticket_status']

            ticket_id = ''
            if 'ticket_id' in body.keys():
                ticket_id = body['ticket_id']

            params = {
                "ticket_id": ticket_id,
                "client_id": body["client_id"],
                "category": body["category"],
                "ticket_topic": body["ticket_topic"]
            }

            self._logger.info(f'Collecting all tickets for client id: {params["client_id"]}...')

            filtered_tickets = self._bruin_repository.get_all_filtered_tickets(params, ticket_status)

            filtered_tickets_response['body'] = filtered_tickets["body"]
            filtered_tickets_response["status"] = filtered_tickets["status"]

            self._logger.info(f'All tickets for client id: {params["client_id"]} sent')

        else:
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = 'You must specify ' \
                                                '{..."body:{"client_id", "category", "ticket_topic",' \
                                                ' "ticket_status":[list of statuses]}...} in the request'
        await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
