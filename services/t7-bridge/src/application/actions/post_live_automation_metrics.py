import json
import logging

from nats.aio.msg import Msg

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)
missing = object()


class PostLiveAutomationMetrics:
    def __init__(self, t7_kre_repository):
        self._t7_kre_repository = t7_kre_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}
        payload = payload.get("body")

        err_body = 'You must specify {.."body": {"ticket_id", "asset_id", "automated_successfully"}..} in the request'
        if not payload:
            logger.error(f"Cannot post live automation metrics using {json.dumps(payload)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = payload.get("ticket_id", missing)
        asset_id = payload.get("asset_id", missing)
        automated_successfully = payload.get("automated_successfully", missing)

        if any(field is missing for field in [ticket_id, asset_id, automated_successfully]):
            logger.error(
                f"Cannot post live automation metrics using {json.dumps(payload)}. "
                f'Need parameters "ticket_id", "asset_id" and "automated_successfully"'
            )
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        post_live_metrics_response = self._t7_kre_repository.post_live_automation_metrics(
            ticket_id, asset_id, automated_successfully
        )

        response = {
            "request_id": request_id,
            "body": post_live_metrics_response["body"],
            "status": post_live_metrics_response["status"],
        }

        await msg.respond(to_json_bytes(response))
        logger.info(f"Live metrics posted for ticket {ticket_id} published in event bus!")
