import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class SaveOutputs:
    def __init__(self, repository):
        self._kre_repository = repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}

        payload = payload.get("body")
        if not payload:
            logger.error(f"Cannot post automation outputs using {json.dumps(payload)}. JSON malformed")
            response["body"] = "You must specify body in the request"
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        post_outputs_response = await self._kre_repository.save_outputs(payload)
        response = {
            "request_id": request_id,
            "body": post_outputs_response["body"],
            "status": post_outputs_response["status"],
        }

        await msg.respond(to_json_bytes(response))
        logger.info(f'Save outputs response for email {payload["email_id"]} published in event bus!')
