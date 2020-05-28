import json


class GetNextResultsForTicketDetail:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_next_results_for_ticket_detail(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }

        request_body = msg.get("body")
        if not request_body:
            self._logger.error(f'Cannot get next results for ticket detail using {json.dumps(msg)}. JSON malformed')
            response["status"] = 400
            response["body"] = (
                'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request'
            )
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        if list(request_body.keys()) != ['ticket_id', 'detail_id', 'service_number']:
            self._logger.info(f'Cannot get next results for ticket detail using {json.dumps(request_body)}. '
                              f'Need "ticket_id", "detail_id", "service_number"')
            response["status"] = 400
            response["body"] = (
                'You must specify {.."body": {"ticket_id", "detail_id", "service_number"}...} in the request'
            )
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        ticket_id = request_body['ticket_id']
        detail_id = request_body['detail_id']
        service_number = request_body['service_number']

        self._logger.info(f'Claiming all available next results for ticket {ticket_id} and detail {detail_id}...')
        next_results = self._bruin_repository.get_next_results_for_ticket_detail(ticket_id, detail_id, service_number)
        self._logger.info(f'Got all available next results for ticket {ticket_id} and detail {detail_id}!')

        response["body"] = next_results["body"]
        response["status"] = next_results["status"]

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Next results for ticket {ticket_id} and detail {detail_id} published in event bus!')
