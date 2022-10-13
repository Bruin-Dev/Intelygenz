import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class MarkEmailAsDone:
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

        if body.get("email_id"):
            email_id = body["email_id"]

            logger.info(f"Marking email: {email_id} as Done")
            result = await self._bruin_repository.mark_email_as_done(email_id)

            response["body"] = result["body"]
            response["status"] = result["status"]
        else:
            logger.error(f"Cannot mark emails as done using {json.dumps(payload)}. JSON malformed")

            response["body"] = "You must include email_id in the request"
            response["status"] = 400

        await msg.respond(to_json_bytes(response))
