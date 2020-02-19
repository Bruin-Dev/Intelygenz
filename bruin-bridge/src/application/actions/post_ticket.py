import json


class PostTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_ticket(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }

        if msg.get("body"):

            payload = msg["body"]

            if not all(key in payload.keys() for key in ("clientId", "category", "services", "contacts")):
                self._logger.info(f'Cannot create ticket using {json.dumps(payload)}. '
                                  f'Need "clientId", "category", "services", "contacts"')
                response["status"] = 400
                response["body"] = 'You must specify "clientId", "category", ' \
                                   '"services", "contacts" in the body'
                await self._event_bus.publish_message(msg['response_topic'], response)
                return

            if "notes" not in payload.keys():
                payload["notes"] = []

            self._logger.info(f'Creating ticket for client id: {payload["clientId"]}...')

            result = self._bruin_repository.post_ticket(payload)

            response['body'] = result["body"]
            response["status"] = result["status"]
            if response["status"] in range(200, 300):
                self._logger.info(f'Ticket created for client id: {payload["clientId"]} with ticket id:'
                                  f' {result["body"]["ticketIds"][0]}')
            else:
                self._logger.error(response['body'])
        else:

            self._logger.error(f'Cannot create a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'You must specify ' \
                               '{.."body":{"clientId", "category", "services", "contacts"}, in the request'

        await self._event_bus.publish_message(msg['response_topic'], response)
