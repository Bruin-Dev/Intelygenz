import json


class PostNote:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_note(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        if msg.get("body") is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], response)
            return
        body = msg['body']
        if all(key in body.keys() for key in ("ticket_id", "note")):

            ticket_id = msg["body"]["ticket_id"]
            note = msg["body"]["note"]

            if len(note) > 1500:
                self._logger.info(f'Cannot post a note to ticket {ticket_id}')
                self._logger.info(f'Message is of length:{len(note)} and exceeds 1500 character limit')

                response["body"] = 'Note exceeds 1500 character limit'
                response["status"] = 400
                await self._event_bus.publish_message(msg['response_topic'], response)
                return

            self._logger.info(f'Putting note in: {ticket_id}...')

            result = self._bruin_repository.post_ticket_note(ticket_id, note)

            response["body"] = result['body']
            response["status"] = result['status']
            self._logger.info(f'Note successfully posted to ticketID:{ticket_id} ')

        else:
            self._logger.error(f'Cannot post a note to ticket using {json.dumps(msg)}. '
                               f'JSON malformed')

            response["body"] = 'You must include "ticket_id" and "note" in the "body" field of the response request'
            response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], response)
