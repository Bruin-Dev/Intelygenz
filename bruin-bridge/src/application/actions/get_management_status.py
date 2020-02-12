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
            'management_status': None,
            'status': None
        }
        if "filters" not in msg.keys():
            self._logger.error(f'Cannot get management status using {json.dumps(msg)}. '
                               f'JSON malformed')
            response["status"] = 400
            response["error_message"] = 'You must specify ' \
                                        '{.."filter":{"client_id", "status", "service_number"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg['filters']

        if not all(key in filters.keys() for key in ("client_id", "status", "service_number")):
            self._logger.info(f'Cannot get management status using {json.dumps(filters)}. '
                              f'Need "client_id", "status", "service_number"')
            response["status"] = 400
            response["error_message"] = 'You must specify "client_id", "status", "service_number" in the filter'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting management status with filters: {json.dumps(filters)}'
        )

        management_status = self._bruin_repository.get_management_status(filters)

        if management_status["status_code"] in range(200, 300):
            response["management_status"] = management_status["body"]
            response["status"] = 200
            self._logger.info(f'Management status found using the filters {json.dumps(filters)}')
        elif management_status["status_code"] == 400:
            response["status"] = 400
            response["error_message"] = f"Bad request when retrieving management status: {management_status['body']}"
            self._logger.error(f'Error trying to get management status: {management_status["body"]}')
        elif management_status["status_code"] == 401:
            response["status"] = 400
            response["error_message"] = f"Authentication error in bruin API."
            print(response)  # Remove
            self._logger.error(f'Error trying to authenticate against bruin API: {management_status["body"]}')
        elif management_status["status_code"] == 503:
            response["status"] = 503
            response["error_message"] = management_status["body"]
            self._logger.info(management_status["body"])
        elif management_status["status_code"] in range(500, 513):
            response["status"] = 500
            response["error_message"] = f"Internal server error from bruin API"
            self._logger.error(f'Error accesing bruin API: {management_status["body"]}')

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f'Management status published in event bus for request {json.dumps(msg)}. '
            f"Message published was {response}"
        )
