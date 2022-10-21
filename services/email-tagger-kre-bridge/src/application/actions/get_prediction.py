import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class GetPrediction:
    def __init__(self, repository):
        self._email_tagger_repository = repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}
        payload = payload.get("body")

        err_body = 'You must specify {.."body": { "email": {"email_id", "subject", ...}}} in the request'
        if not payload:
            logger.error(f"Cannot get prediction using {json.dumps(payload)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        email_data = payload.get("email")
        if not email_data:
            logger.error(f'Cannot get prediction using {json.dumps(payload)}. Need parameters "email"')
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        email_id = email_data.get("email_id")
        if not email_id:
            logger.error(f'Cannot get prediction using {json.dumps(payload)}. Need parameters "email_id"')
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        prediction = await self._email_tagger_repository.get_prediction(payload)

        response = {"request_id": request_id, "body": prediction["body"], "status": prediction["status"]}

        await msg.respond(to_json_bytes(response))
        logger.info(f"Prediction for email {email_id} published in event bus!")
