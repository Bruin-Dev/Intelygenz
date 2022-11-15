import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class PostAutomationMetrics:
    def __init__(self, t7_kre_repository):
        self._t7_kre_repository = t7_kre_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}
        payload = payload.get("body")

        err_body = 'You must specify {.."body": {"ticket_id", "ticket_rows"}..} in the request'
        if not payload:
            logger.error(f"Cannot post automation metrics using {json.dumps(payload)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        if not all(key in payload.keys() for key in ("ticket_id", "ticket_rows")):
            logger.error(
                f"Cannot post automation metrics using {json.dumps(payload)}. "
                f'Need parameter "ticket_id" and "ticket_rows"'
            )
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        post_metrics_response = self._t7_kre_repository.post_automation_metrics(payload)
        response = {
            "request_id": request_id,
            "body": post_metrics_response["body"],
            "status": post_metrics_response["status"],
        }

        await msg.respond(to_json_bytes(response))
        logger.info(f'Metrics posted for ticket {payload["ticket_id"]} published in event bus!')
