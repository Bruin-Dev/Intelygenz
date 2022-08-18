import json


class GetDRIParameters:
    def __init__(self, logger, event_bus, dri_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._dri_repository = dri_repository

    async def get_dri_parameters(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}
        if "body" not in msg.keys():
            self._logger.error(f"Cannot get DRI parameters using {json.dumps(msg)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'You must specify {.."body":{"serial_number", "parameter_set"}...} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        params = msg["body"]

        if not all(key in params.keys() for key in ("serial_number", "parameter_set")):
            self._logger.error(
                f'Cannot get DRI parameters using {json.dumps(params)}. Need "serial_number" and ' f'"parameter_set"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "serial_number" and "parameter_set" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        serial_number = params["serial_number"]
        parameter_set = params["parameter_set"]

        self._logger.info(f"Getting DRI parameters for serial_number {serial_number}")

        dri_parameters = await self._dri_repository.get_dri_parameters(serial_number, parameter_set)

        response["status"] = dri_parameters["status"]
        response["body"] = dri_parameters["body"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f"The DRI parameters response for serial {serial_number} was published in "
            f"event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
