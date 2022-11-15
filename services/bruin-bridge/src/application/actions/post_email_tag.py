import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostEmailTag:
    def __init__(self, bruin_repository):
        self._bruin_repository = bruin_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}
        body = payload.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in body.keys() for key in ("email_id", "tag_id")):
            logger.error(f"Cannot add a tag to email using {json.dumps(payload)}. JSON malformed")

            response["body"] = 'You must include "email_id" and "tag_id" in the "body" field of the response request'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        email_id = body.get("email_id")
        tag_id = body.get("tag_id")

        logger.info(f'Adding tag_id "{tag_id}" to email_id "{email_id}"...')

        result = await self._bruin_repository.post_email_tag(email_id, tag_id)

        response["body"] = result["body"]
        response["status"] = result["status"]
        if response["status"] in range(200, 300):
            logger.info(f"Tags successfully added to email_id: {email_id} ")
        else:
            logger.error(f"Error adding tags to email: Status: {response['status']} body: {response['body']}")

        await msg.respond(to_json_bytes(response))
