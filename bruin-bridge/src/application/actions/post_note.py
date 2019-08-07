import json


class PostNote:

    def __init__(self, logger, event_bus, bruin_client):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_client = bruin_client

    async def post_note(self, msg):
        msg_dict = json.loads(msg)
        ticket_id = msg_dict["ticket_id"]
        note = msg_dict["note"]
        self._logger.info(f'Putting note in: {ticket_id}...')
        status = 500
        result = self._bruin_client.post_ticket_note(ticket_id, note)
        if result is not None:
            status = 200
        response = {
            'request_id': msg_dict['request_id'],
            'status': status
        }
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
        self._logger.info(f'Note put in: {ticket_id}!')
