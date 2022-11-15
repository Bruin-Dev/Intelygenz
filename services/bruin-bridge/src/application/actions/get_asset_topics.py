import json
import logging
from http import HTTPStatus

from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

NO_BODY_MSG = 'Must include {.."body":{"client_id", "service_number"}, ..} in request'
MISSING_PARAMS_MSG = "You must include 'client_id' and 'service_number' in the 'body' field of the response request"
WRONG_CLIENT_ID_MSG = "body.client_id should be an int"
EMPTY_SERVICE_NUMBER_MSG = "body.service_number can't be empty"

logger = logging.getLogger(__name__)


class GetAssetTopics:
    def __init__(self, bruin_repository: BruinRepository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        payload = payload.get("body")

        if payload is None:
            response["status"] = HTTPStatus.BAD_REQUEST
            response["body"] = NO_BODY_MSG
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in payload.keys() for key in ("client_id", "service_number")):
            logger.error(f"Cannot get asset topics using {json.dumps(payload)}. " f"JSON malformed")

            response["body"] = MISSING_PARAMS_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await msg.respond(to_json_bytes(response))
            return

        try:
            client_id = int(payload.get("client_id"))
        except ValueError:
            logger.error(f"body.client_id {payload.get('client_id')} should be an int.")
            response["body"] = WRONG_CLIENT_ID_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await msg.respond(to_json_bytes(response))
            return

        service_number = payload.get("service_number")
        if not service_number:
            logger.error(f"body.service_number can't be empty")
            response["body"] = EMPTY_SERVICE_NUMBER_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await msg.respond(to_json_bytes(response))
            return

        logger.info(f"Getting asset topics for client '{client_id}', service number '{service_number}'")
        result = await self._bruin_repository.get_asset_topics(payload)

        response["body"] = result.body
        response["status"] = result.status
        await msg.respond(to_json_bytes(response))
