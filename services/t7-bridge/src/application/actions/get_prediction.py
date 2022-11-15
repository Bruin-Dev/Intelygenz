import json
import logging

from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetPrediction:
    def __init__(self, t7_kre_repository):
        self._t7_kre_repository = t7_kre_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        request_id = payload["request_id"]
        response = {"request_id": request_id, "body": None, "status": None}
        payload = payload.get("body")

        err_body = 'You must specify {.."body": {"ticket_id", "ticket_rows", "assets_to_predict"}..} in the request'
        if not payload:
            logger.error(f"Cannot get prediction using {json.dumps(payload)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        ticket_id = payload.get("ticket_id")
        ticket_rows = payload.get("ticket_rows")
        assets_to_predict = payload.get("assets_to_predict")

        if not (ticket_id and ticket_rows and assets_to_predict):
            logger.error(
                f"Cannot get prediction using {json.dumps(payload)}. "
                f'Need parameters "ticket_id", "ticket_rows" and "assets_to_predict"'
            )
            response["body"] = err_body
            response["status"] = 400
            await msg.respond(to_json_bytes(response))
            return

        prediction = self._t7_kre_repository.get_prediction(ticket_id, ticket_rows, assets_to_predict)

        response = {"request_id": request_id, "body": prediction["body"], "status": prediction["status"]}

        await msg.respond(to_json_bytes(response))
        logger.info(f"Prediction for ticket {ticket_id} published in event bus!")
