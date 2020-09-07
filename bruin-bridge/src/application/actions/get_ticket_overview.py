class GetTicketOverview:

    def __init__(self, logger, config, event_bus, bruin_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_ticket_overview(self, msg: dict):

        ticket_response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        body = msg.get("body")

        if body is None:
            ticket_response["status"] = 400
            ticket_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], ticket_response)
            return

        if 'ticket_id' not in body.keys():
            ticket_response["status"] = 400
            ticket_response["body"] = 'Must include "ticket_id" in body'
            await self._event_bus.publish_message(msg['response_topic'], ticket_response)
            return

        ticket_id = body["ticket_id"]

        self._logger.info(f'Getting ticket for ticket_id: {ticket_id}...')

        ticket = await self._bruin_repository.get_ticket_overview(ticket_id)

        self._logger.info(f'Got ticket overview for ticket id: {ticket_id}...')

        await self._event_bus.publish_message(msg['response_topic'], ticket)
