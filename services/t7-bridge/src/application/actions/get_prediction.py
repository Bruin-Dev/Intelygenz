import json


class GetPrediction:
    def __init__(self, logger, config, event_bus, t7_kre_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_kre_repository = t7_kre_repository

    async def get_prediction(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        err_body = 'You must specify {.."body": {"ticket_id", "ticket_rows", "assets_to_predict"}..} in the request'
        msg_body = msg.get("body")
        if not msg_body:
            self._logger.error(f"Cannot get prediction using {json.dumps(msg)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg_body.get("ticket_id")
        ticket_rows = msg_body.get("ticket_rows")
        assets_to_predict = msg_body.get("assets_to_predict")

        if not (ticket_id and ticket_rows and assets_to_predict):
            self._logger.error(
                f"Cannot get prediction using {json.dumps(msg_body)}. "
                f'Need parameters "ticket_id", "ticket_rows" and "assets_to_predict"'
            )
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        prediction = self._t7_kre_repository.get_prediction(ticket_id, ticket_rows, assets_to_predict)

        response = {"request_id": msg["request_id"], "body": prediction["body"], "status": prediction["status"]}

        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Prediction for ticket {ticket_id} published in event bus!")