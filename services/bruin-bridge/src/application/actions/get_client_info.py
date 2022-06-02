import json


class GetClientInfo:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_client_info(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}
        if "body" not in msg.keys():
            self._logger.error(f"Cannot get bruin client info using {json.dumps(msg)}. " f"JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"service_number":...}} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = msg["body"]

        if "service_number" not in filters.keys():
            self._logger.error(f'Cannot get bruin client info using {json.dumps(filters)}. Need "service_number"')
            response["status"] = 400
            response["body"] = 'You must specify "service_number" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(f"Getting Bruin client ID with filters: {json.dumps(filters)}")

        client_info = await self._bruin_repository.get_client_info(filters)

        response["body"] = client_info["body"]
        response["status"] = client_info["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f"Bruin client_info published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
