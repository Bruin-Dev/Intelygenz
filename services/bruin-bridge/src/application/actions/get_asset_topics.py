import json
from http import HTTPStatus

from application.repositories.bruin_repository import BruinRepository

NO_BODY_MSG = "Must include {..\"body\":{\"client_id\", \"service_number\"}, ..} in request"
MISSING_PARAMS_MSG = "You must include 'client_id' and 'service_number' in the 'body' field of the response request"
WRONG_CLIENT_ID_MSG = "body.client_id should be an int"
EMPTY_SERVICE_NUMBER_MSG = "body.service_number can't be empty"


class GetAssetTopics:
    def __init__(self, logger, event_bus, bruin_repository: BruinRepository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_asset_topics(self, msg: dict):
        response = {
            "request_id": msg["request_id"],
            "body": None,
            "status": None
        }
        payload = msg.get("body")

        if payload is None:
            response["status"] = HTTPStatus.BAD_REQUEST
            response["body"] = NO_BODY_MSG
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if not all(key in payload.keys() for key in ("client_id", "service_number")):
            self._logger.error(f"Cannot get asset topics using {json.dumps(msg)}. "
                               f"JSON malformed")

            response["body"] = MISSING_PARAMS_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        client_id = payload.get("client_id")
        if type(client_id) is not int:
            self._logger.error(f"body.client_id {client_id} should be an int.")
            response["body"] = WRONG_CLIENT_ID_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        service_number = payload.get("service_number")
        if not service_number:
            self._logger.error(f"body.service_number can't be empty")
            response["body"] = EMPTY_SERVICE_NUMBER_MSG
            response["status"] = HTTPStatus.BAD_REQUEST
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        self._logger.info(f"Getting asset topics for client '{client_id}', service number '{service_number}'")
        result = await self._bruin_repository.get_asset_topics(payload)

        response["body"] = result.body
        response["status"] = result.status
        await self._event_bus.publish_message(msg["response_topic"], response)
