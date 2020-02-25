import json


class GetTicketTaskHistory:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_ticket_task_history(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if "filters" not in msg.keys():
            self._logger.error(f'Cannot get ticket task history using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'You must specify ' \
                               '{.."filter":{"ticket_id"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg['filters']

        if "ticket_id" not in filters.keys():
            self._logger.info(f'Cannot get get ticket task history using {json.dumps(filters)}. '
                              f'Need "ticket_id"')
            response["status"] = 400
            response["body"] = 'You must specify "ticket_id" in the filter'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting ticket task history with filters: {json.dumps(filters)}'
        )

        ticket_task_history = self._bruin_repository.get_ticket_task_history(filters)

        response["body"] = ticket_task_history["body"]
        response["status"] = ticket_task_history["status_code"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'get ticket task history published in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
