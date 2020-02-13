import json


class ChangeDetailWorkQueue:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def change_detail_work_queue(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if not msg.get("filters"):
            self._logger.error(f'Cannot get management status using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must specify ' \
                                        '{.."filters":{"service_number", "ticket_id",' \
                                        ' "detail_id","queue_name"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg['filters']

        if not all(key in filters.keys() for key in ("service_number", "ticket_id", "detail_id", "queue_name")):
            self._logger.error(f'Cannot get management status using {json.dumps(filters)}. '
                              f'Need "client_id", "status", "service_number"')
            response["status"] = 400
            response["error_message"] = 'You must specify ' \
                                        '{.."filter":{"service_number", "ticket_id",' \
                                        ' "detail_id","queue_name"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Changing work queue with filters: {json.dumps(filters)}'
        )

        result = self._bruin_repository.change_detail_work_queue(filters)

        response["status"] = result["status_code"]
        response["body"] = result["body"]
        await self._event_bus.publish_message(response_topic, response)

        self._logger.info(f'Result of changing work queue published in event bus {json.dumps(msg)}')
