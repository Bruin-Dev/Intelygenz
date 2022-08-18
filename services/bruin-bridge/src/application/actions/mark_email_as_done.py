import json


class MarkEmailAsDone:
    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def mark_email_as_done(self, msg):
        response = {"request_id": msg["request_id"], "status": None}
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        if body.get("email_id"):
            email_id = body["email_id"]

            self._logger.info(f"Marking email: {email_id} as Done")
            result = await self._bruin_repository.mark_email_as_done(email_id)

            response["body"] = result["body"]
            response["status"] = result["status"]
        else:
            self._logger.error(f"Cannot mark emails as done using {json.dumps(msg)}. JSON malformed")

            response["body"] = "You must include email_id in the request"
            response["status"] = 400

        await self._event_bus.publish_message(msg["response_topic"], response)
