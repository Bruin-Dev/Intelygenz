class PostTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_ticket(self, msg: dict):
        client_id = msg["clientId"]
        category = msg["category"]
        services = msg["services"]
        notes = []
        if "notes" in msg.keys():
            notes = msg["notes"]
        contacts = msg["contacts"]

        self._logger.info(f'Creating note for client id: {client_id}...')
        status = 500
        result = self._bruin_repository.post_ticket(client_id, category, services, notes, contacts)
        if result is not None:
            self._logger.info(f'Ticket created for client id: {client_id} with ticket id: {result["ticketIds"][0]}')
            status = 200
        response = {
            'request_id': msg['request_id'],
            'ticketIds': result,
            'status': status
        }
        await self._event_bus.publish_message(msg['response_topic'], response)
