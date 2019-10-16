import json


class PostTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_ticket(self, msg):
        msg_dict = json.loads(msg)
        client_id = msg_dict["clientId"]
        category = msg_dict["category"]
        services = msg_dict["services"]
        notes = []
        if "notes" in msg_dict.keys():
            notes = msg_dict["notes"]
        contacts = msg_dict["contacts"]

        self._logger.info(f'Creating note for client id: {client_id}...')
        status = 500
        result = self._bruin_repository.post_ticket(client_id, category, services, notes, contacts)
        if result is not None:
            status = 200
        response = {
            'request_id': msg_dict['request_id'],
            'ticketIds': result,
            'status': status
        }
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
        self._logger.info(f'Ticket created for client id: {client_id} with ticket id: {result["ticketIds"][0]}')
