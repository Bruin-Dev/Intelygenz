import json


class SaveMetrics:
    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def save_metrics(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        err_body = 'You must specify {.."body": {"original_email": {...}, "ticket": {...}}} in the request'
        msg_body = msg.get("body")
        if not msg_body:
            self._logger.error(f"Cannot post automation metrics using {json.dumps(msg)}. JSON malformed")
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        if not all(key in msg_body.keys() for key in ("original_email", "ticket")):
            self._logger.error(
                f"Cannot save metrics using {json.dumps(msg_body)}. " f'Need parameter "original_email" and "ticket"'
            )
            response["body"] = err_body
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        email_data = msg_body.get("original_email")
        ticket_data = msg_body.get("ticket")
        post_metrics_response = await self._kre_repository.save_metrics(email_data, ticket_data)
        response = {
            "request_id": msg["request_id"],
            "body": post_metrics_response["body"],
            "status": post_metrics_response["status"],
        }

        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f'Metrics posted for email {email_data["email"]["email_id"]} published in event bus!')
