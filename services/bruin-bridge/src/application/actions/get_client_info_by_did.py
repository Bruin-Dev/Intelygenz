import json


class GetClientInfoByDID:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_client_info_by_did(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}
        if "body" not in msg.keys():
            self._logger.error(f"Cannot get Bruin client info by DID using {json.dumps(msg)}. " f"JSON malformed")
            response["status"] = 400
            response["body"] = "You must specify " '{.."body":{"did":...}} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return

        body = msg["body"]

        if "did" not in body.keys():
            self._logger.error(f'Cannot get Bruin client info by DID using {json.dumps(body)}. Need "did"')
            response["status"] = 400
            response["body"] = 'You must specify "did" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        self._logger.info(f"Getting Bruin client info by DID with body: {json.dumps(body)}")

        client_info = await self._bruin_repository.get_client_info_by_did(body["did"])

        response["body"] = client_info["body"]
        response["status"] = client_info["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f"Bruin client_info_by_did published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
