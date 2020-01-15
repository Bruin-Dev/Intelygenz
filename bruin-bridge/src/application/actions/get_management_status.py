import json


class GetManagementStatus:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_management_status(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        filters = msg['filters']
        response = {
            'request_id': request_id,
            'management_status': None,
            'status': None
        }

        if "client_id" not in filters.keys():
            self._logger.error(f'Cannot get management status using {json.dumps(filters)}. Need client_id')
            response["status"] = 400
            response["error_message"] = "You must specify client_id in the filter"
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(
            f'Getting management status with filters: {json.dumps(filters)}'
        )

        management_status = self._bruin_repository.get_management_status(filters)
        if management_status:
            status = 200
            self._logger.info(f'Management status found using the filters {json.dumps(filters)}')
        else:
            status = 500
            self._logger.info(f'Error trying to get management status using filters: {json.dumps(filters)}.')

        response["status"] = status
        response["management_status"] = management_status
        await self._event_bus.publish_message(response_topic, response)

        self._logger.info(f'Management status published in event bus')
