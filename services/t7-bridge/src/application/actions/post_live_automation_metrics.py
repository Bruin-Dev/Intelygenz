import json

missing = object()


class PostLiveAutomationMetrics:
    def __init__(self, logger, config, event_bus, t7_kre_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_kre_repository = t7_kre_repository

    async def post_live_automation_metrics(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        err_body = 'You must specify {.."body": {"ticket_id", "asset_id", "automated_successfully"}..} in the request'
        msg_body = msg.get("body")
        if not msg_body:
            self._logger.error(f"Cannot post live automation metrics using {json.dumps(msg)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg_body.get("ticket_id", missing)
        asset_id = msg_body.get("asset_id", missing)
        automated_successfully = msg_body.get("automated_successfully", missing)

        if any(field is missing for field in [ticket_id, asset_id, automated_successfully]):
            self._logger.error(
                f"Cannot post live automation metrics using {json.dumps(msg_body)}. "
                f'Need parameters "ticket_id", "asset_id" and "automated_successfully"'
            )
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        post_live_metrics_response = self._t7_kre_repository.post_live_automation_metrics(
            ticket_id, asset_id, automated_successfully
        )

        response = {
            "request_id": msg["request_id"],
            "body": post_live_metrics_response["body"],
            "status": post_live_metrics_response["status"],
        }

        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Live metrics posted for ticket {ticket_id} published in event bus!")
