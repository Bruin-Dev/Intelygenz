import json


class PostTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_ticket(self, msg: dict):
        response_topic = msg['response_topic']

        response = {
            'request_id': msg['request_id'],
            'ticketIds': None,
            'status': None
        }

        if "payload" not in msg.keys():
            self._logger.error(f'Cannot create a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must specify ' \
                                        '{.."payload":{"clientId", "category", "services", "contacts"}, in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        payload = msg["payload"]

        if not all(key in payload.keys() for key in ("clientId", "category", "services", "contacts")):
            self._logger.info(f'Cannot create ticket using {json.dumps(payload)}. '
                              f'Need "clientId", "category", "services", "contacts"')
            response["status"] = 400
            response["error_message"] = 'You must specify "clientId", "category", "services", "contacts" in the payload'
            await self._event_bus.publish_message(response_topic, response)
            return

        if "notes" not in payload.keys():
            payload["notes"] = []

        self._logger.info(f'Creating ticket for client id: {payload["clientId"]}...')

        result = self._bruin_repository.post_ticket(payload)

        if result["status_code"] in range(200, 300):
            response['ticketIds'] = result["body"]
            response["status"] = 200
            self._logger.info(f'Ticket created for client id: {payload["clientId"]} with ticket id:'
                              f' {result["body"]["ticketIds"][0]}')
        elif result["status_code"] == 400:
            response["status"] = 400
            response["error_message"] = f"Bad request when posting ticket: {result['body']}"
            self._logger.error(f'Error trying to get ticket list: {result["body"]}')
        elif result["status_code"] == 401:
            response["status"] = 400
            response["error_message"] = f"Authentication error in bruin API."
            self._logger.error(f'Error trying to authenticate against bruin API: {result["body"]}')
        elif result["status_code"] in range(500, 513):
            response["status"] = 500
            response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accessing bruin API: {result["body"]}')

        await self._event_bus.publish_message(response_topic, response)
