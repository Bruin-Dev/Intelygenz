import json


class GetInference:
    def __init__(self, logger, config, event_bus, repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._kre_repository = repository

    async def get_inference(self, msg: dict):
        """Get the email inference from the KRE process and publish it.

        Args:
            msg (dict): The request.
        """
        response = {
            "request_id": msg["request_id"],
            "body": None,
            "status": None,
        }

        response_topic = msg["response_topic"]

        msg_body = msg.get("body", {})
        email_id = msg_body.get("email_id")
        if not msg_body or not email_id:
            self._logger.error(f'Cannot get inference using {json.dumps(msg)}. JSON malformed')
            response['body'] = 'You must specify {.."body": { "email_id", "subject", ...}} in the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        inference = await self._kre_repository.get_email_inference(msg_body)
        response["body"] = inference["body"]
        response["status"] = inference["status"]

        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Inference for email {email_id} published in event bus!")
