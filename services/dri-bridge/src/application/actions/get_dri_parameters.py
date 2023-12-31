import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetDRIParameters:
    def __init__(self, dri_repository):
        self._dri_repository = dri_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if "body" not in payload.keys():
            logger.error(f"Cannot get DRI parameters using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'You must specify {.."body":{"serial_number", "parameter_set"}...} in the request'
            await msg.respond(to_json_bytes(response))
            return

        params = payload["body"]

        if not all(key in params.keys() for key in ("serial_number", "parameter_set")):
            logger.error(
                f'Cannot get DRI parameters using {json.dumps(params)}. Need "serial_number" and ' f'"parameter_set"'
            )
            response["status"] = 400
            response["body"] = 'You must specify "serial_number" and "parameter_set" in the body'
            await msg.respond(to_json_bytes(response))
            return

        serial_number = params["serial_number"]
        parameter_set = params["parameter_set"]

        logger.info(f"Getting DRI parameters for serial_number {serial_number}")

        dri_parameters = await self._dri_repository.get_dri_parameters(serial_number, parameter_set)

        response["status"] = dri_parameters["status"]
        response["body"] = dri_parameters["body"]

        await msg.respond(to_json_bytes(response))
        logger.info(
            f"The DRI parameters response for serial {serial_number} was published in "
            f"event bus for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
