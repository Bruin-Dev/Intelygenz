import json


class PostEmailTag:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_email_tag(self, msg: dict):
        response = {"request_id": msg["request_id"], "body": None, "status": None}
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if not all(key in body.keys() for key in ("email_id", "tag_id")):
            self._logger.error(f"Cannot add a tag to email using {json.dumps(msg)}. " f"JSON malformed")

            response["body"] = 'You must include "email_id" and "tag_id" in the "body" field of the response request'
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        email_id = body.get("email_id")
        tag_id = body.get("tag_id")

        self._logger.info(f'Adding tag_id "{tag_id}" to email_id "{email_id}"...')

        result = await self._bruin_repository.post_email_tag(email_id, tag_id)

        response["body"] = result["body"]
        response["status"] = result["status"]
        if response["status"] in range(200, 300):
            self._logger.info(f"Tags successfully added to email_id: {email_id} ")
        else:
            self._logger.error(f"Error adding tags to email: Status: {response['status']} body: {response['body']}")

        await self._event_bus.publish_message(msg["response_topic"], response)
