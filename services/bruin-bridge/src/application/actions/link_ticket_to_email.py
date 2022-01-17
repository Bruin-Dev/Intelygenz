import json


class LinkTicketToEmail:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def link_ticket_to_email(self, msg: dict):
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

        if not all(key in body.keys() for key in ("ticket_id", "email_id")):
            self._logger.error(f'Cannot link ticket to email using {json.dumps(msg)}. '
                               f'JSON malformed')

            response["body"] = 'You must include "ticket_id" and "email_id" in the "body" field of the request'
            response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        ticket_id = msg["body"]["ticket_id"]
        email_id = msg["body"]["email_id"]

        self._logger.info(f'Linking ticket {ticket_id} to email {email_id}...')

        result = await self._bruin_repository.link_ticket_to_email(ticket_id, email_id)

        response["body"] = result['body']
        response["status"] = result['status']
        self._logger.info(f'Ticket {ticket_id} successfully posted to email_id:{email_id} ')

        await self._event_bus.publish_message(msg['response_topic'], response)
