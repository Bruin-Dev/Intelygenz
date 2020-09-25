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
        body = msg.get("body")

        if body is None:
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
            return
        if not all(key in body.keys() for key in ("client_id", "category", "ticket_topic", "ticket_status")):
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["body"] = 'You must specify ' \
                                                '{..."body:{"client_id", "category", "ticket_topic",' \
                                                ' "ticket_status":[list of statuses]}...} in the request'
            await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
            return

        ticket_status = body['ticket_status']

        params = {
            "client_id": body["client_id"],
            "category": body["category"],
            "ticket_topic": body["ticket_topic"]
        }

        ticket_id = body.get('ticket_id')
        if ticket_id:
            params['ticket_id'] = ticket_id

        service_number = body.get('service_number')
        if service_number:
            params['service_number'] = service_number

        # Valid date format: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        start_date = body.get("start_date")
        end_date = body.get("end_date")
        if start_date and end_date:
            params["start_date"] = start_date
            params["end_date"] = end_date

        self._logger.info(f'Collecting all tickets for client id: {params["client_id"]}...')

        filtered_tickets = await self._bruin_repository.get_all_filtered_tickets(params, ticket_status)

        filtered_tickets_response = {**filtered_tickets_response, **filtered_tickets}

        self._logger.info(f'All tickets for client id: {params["client_id"]} sent')

        await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
