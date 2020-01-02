class PostNote:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_note(self, msg: dict):
        ticket_id = msg["ticket_id"]
        note = msg["note"]
        self._logger.info(f'Putting note in: {ticket_id}...')
        status = 500
        result = None

        if len(note) < 1500:
            result = self._bruin_repository.post_ticket_note(ticket_id, note)
        else:
            self._logger.info(f'Message is of length:{len(note)} and exceeds 1500 character limit')
            status = 400

        if result is not None:
            self._logger.info(f'Note put in: {ticket_id}!')
            status = 200
        response = {
            'request_id': msg['request_id'],
            'status': status
        }
        await self._event_bus.publish_message(msg['response_topic'], response)
