import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetInference:
    def __init__(self, repository):
        self._kre_repository = repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {
            "request_id": request_id,
            "body": None,
            "status": None,
        }

        payload = payload.get("body")
        email_id = payload.get("email_id")
        if not payload or not email_id:
            logger.error(f"Cannot get inference using {json.dumps(payload)}. JSON malformed")
            response["body"] = 'You must specify {.."body": { "email_id", "subject", ...}} in the request'
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        inference = await self._kre_repository.get_email_inference(payload)
        response["body"] = inference["body"]
        response["status"] = inference["status"]

        await msg.respond(to_json_bytes(response))
        logger.info(f"Inference for email {email_id} published in event bus!")
