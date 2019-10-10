import json


class PostNote:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_note(self, msg):
        msg_dict = json.loads(msg)
        ticket_id = msg_dict["ticket_id"]
        note = msg_dict["note"]
        self._logger.info(f'Putting note in: {ticket_id}...')
        status = 500
        result = None

        if len(note) < 1500:
            result = self._bruin_repository.post_ticket_note(ticket_id, note)
        else:
            self._logger.info(f'Message is of length:{len(note)} and exceeds 1500 character limit')
            status = 400

        if result is not None:
            status = 200
        response = {
            'request_id': msg_dict['request_id'],
            'status': status
        }
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
        self._logger.info(f'Note put in: {ticket_id}!')
