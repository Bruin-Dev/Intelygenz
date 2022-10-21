import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class SaveMetrics:
    def __init__(self, repository):
        self._email_tagger_repository = repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}
        payload = payload.get("body")

        err_body = 'You must specify {.."body": {"original_email": {...}, "ticket": {...}}} in the request'
        if not payload:
            logger.error(f"Cannot post automation metrics using {json.dumps(payload)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in payload.keys() for key in ("original_email", "ticket")):
            logger.error(
                f"Cannot save metrics using {json.dumps(payload)}. Need parameter 'original_email' and 'ticket'"
            )
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        email_data = payload.get("original_email")
        ticket_data = payload.get("ticket")
        post_metrics_response = await self._email_tagger_repository.save_metrics(email_data, ticket_data)
        response = {
            "request_id": request_id,
            "body": post_metrics_response["body"],
            "status": post_metrics_response["status"],
        }

        await msg.respond(to_json_bytes(response))
        logger.info(f'Metrics posted for email {email_data["email"]["email_id"]} published in event bus!')
