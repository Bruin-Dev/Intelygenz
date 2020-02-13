import json


class GetManagementStatus:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_management_status(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }
        if "filters" not in msg.keys():
            self._logger.error(f'Cannot get management status using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["body"] = 'You must specify ' \
                               '{.."filter":{"client_id", "status", "service_number"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg['filters']

        if not all(key in filters.keys() for key in ("client_id", "status", "service_number")):
            self._logger.info(f'Cannot get management status using {json.dumps(filters)}. '
                              f'Need "client_id", "status", "service_number"')
            response["status"] = 400
            response["body"] = 'You must specify "client_id", "status", "service_number" in the filter'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting management status with filters: {json.dumps(filters)}'
        )

        management_status = self._bruin_repository.get_management_status(filters)

        response["body"] = management_status["body"]
        response["status"] = management_status["status_code"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'Management status published in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
