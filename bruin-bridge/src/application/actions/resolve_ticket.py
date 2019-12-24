import json


class ResolveTicket:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def resolve_ticket(self, msg):
        msg_dict = json.loads(msg)
        ticket_id = msg_dict["ticket_id"]
        detail_id = msg_dict["detail_id"]

        self._logger.info(f'Updating the ticket status for ticket id: {ticket_id} to RESOLVED')
        status = 500
        result = self._bruin_repository.resolve_ticket(ticket_id, detail_id)
        if result is not None:
            self._logger.info(f'Status: RESOLVED')
            status = 200
        response = {
            'request_id': msg_dict['request_id'],
            'status': status
        }
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(response, default=str))
