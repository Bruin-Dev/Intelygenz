import json


class ResolveTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def resolve_ticket(self, msg):
        response = {
            'request_id': msg['request_id'],
            'status': None
        }
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        if body.get("ticket_id") and body.get("detail_id"):

            ticket_id = body["ticket_id"]
            detail_id = body["detail_id"]

            self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to RESOLVED')
            result = await self._bruin_repository.resolve_ticket(ticket_id, detail_id)

            response['body'] = result['body']
            response["status"] = result["status"]
        else:
            self._logger.error(f'Cannot resolve a ticket using {json.dumps(msg)}. '
                               f'JSON malformed')

            response['body'] = 'You must include ticket_id and detail_id in the request'
            response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], response)
