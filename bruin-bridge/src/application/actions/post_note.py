import json


class PostNote:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_note(self, msg: dict):
        response_topic = msg['response_topic']

        response = {
            'request_id': msg['request_id'],
            'status': None
        }

        if "ticket_id" not in msg.keys() or "note" not in msg.keys():
            self._logger.error(f'Cannot post a note to ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must include "ticket_id" and "note" in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg["ticket_id"]
        note = msg["note"]

        if len(note) > 1500:
            self._logger.info(f'Cannot post a note to ticket {ticket_id}')
            self._logger.info(f'Message is of length:{len(note)} and exceeds 1500 character limit')

            response["status"] = 400
            response["error_message"] = 'Note exceeds 1500 character limit'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(f'Putting note in: {ticket_id}...')

        result = self._bruin_repository.post_ticket_note(ticket_id, note)

        if result["status_code"] in range(200, 300):
            response["status"] = 200
            self._logger.info(f'Note successfully posted to ticketID:{ticket_id} ')
        elif result["status_code"] == 400:
            response["status"] = 400
            response["error_message"] = f"Bad request when posting note to ticketID: {ticket_id}"
            self._logger.error(f'Error trying to post ticket to ticketID: {ticket_id}')
            self._logger.error(f'Error received: {result["body"]}')
        elif result["status_code"] == 401:
            response["status"] = 400
            response["error_message"] = f"Authentication error in bruin API."
            self._logger.error(f'Error trying to authenticate against bruin API: {result["body"]}')
        elif result["status_code"] in range(500, 513):
            response["status"] = 500
            response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accessing bruin API: {result["body"]}')

        await self._event_bus.publish_message(response_topic, response)
