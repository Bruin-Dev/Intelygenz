import json


class MarkEmailAsRead:
    def __init__(self, config, event_bus, logger, email_reader_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._email_reader_repository = email_reader_repository

    async def mark_email_as_read(self, msg):
        response = {"request_id": msg["request_id"], "body": None, "status": None}

        if msg.get("body") is None:
            self._logger.error(f"Cannot mark email as read using {json.dumps(msg)}. Must include body in request")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        payload = msg["body"]
        if not all(key in payload.keys() for key in ("msg_uid", "email_account")):
            self._logger.error(f"Cannot mark email as read using {json.dumps(msg)}. JSON malformed")

            response["body"] = (
                'You must include "msg_uid" and "email_account" ' 'in the "body" field of the response request'
            )
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        msg_uid = payload["msg_uid"]
        email_account = payload["email_account"]

        self._logger.info(f"Attempting to mark message {msg_uid} from email account {email_account} as read")

        mark_as_read_response = await self._email_reader_repository.mark_as_read(msg_uid, email_account)
        response["body"] = mark_as_read_response["body"]
        response["status"] = mark_as_read_response["status"]

        self._logger.info(
            f"Received the following from attempting to mark message {msg_uid} as read: "
            f'{json.dumps(response["body"], indent=2)}'
        )
        await self._event_bus.publish_message(msg["response_topic"], response)
