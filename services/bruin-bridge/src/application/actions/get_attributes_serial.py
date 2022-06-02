import json


class GetAttributeSerial:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_attributes_serial(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        filters = msg.get("body")
        if "body" not in msg.keys():
            self._logger.error(f"Cannot get attribute's serial number using {json.dumps(msg)}. " f"JSON malformed")
            response["status"] = 400
            response["body"] = (
                "You must specify " '{.."body":{"client_id", "status", "service_number"}...} in the request'
            )
            await self._event_bus.publish_message(response_topic, response)
            return

        if not all(key in filters.keys() for key in ("client_id", "status", "service_number")):
            self._logger.info(
                f"Cannot get attribute's serial number using {json.dumps(filters)}. "
                f'Need "client_id", "status", "service_number"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "client_id", "status", "service_number" in the filter'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(f"'Getting attribute's serial number with filters: {json.dumps(filters)}'")

        get_attributes_serial = await self._bruin_repository.get_attributes_serial(filters)

        response["body"] = get_attributes_serial["body"]
        response["status"] = get_attributes_serial["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f"'Attribute's serial number published in event bus for request {json.dumps(msg)}. '"
            f"Message published was {response}"
        )
