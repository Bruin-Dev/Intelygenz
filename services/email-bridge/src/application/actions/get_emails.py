import json


class GetEmails:
    def __init__(self, config, event_bus, logger, email_reader_repository):
        self._config = config
        self._event_bus = event_bus
        self._logger = logger
        self._email_reader_repository = email_reader_repository

    async def get_unread_emails(self, msg):
        response = {"request_id": msg["request_id"], "body": None, "status": None}

        if msg.get("body") is None:
            self._logger.error(f"Cannot get unread emails with {json.dumps(msg)}. Must include body in request")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        payload = msg["body"]
        if not all(key in payload.keys() for key in ("email_account", "email_filter", "lookup_days")):
            self._logger.error(f"Cannot get unread emails with {json.dumps(msg)}. JSON malformed")

            response["body"] = (
                'You must include "email_account", "email_filter" and "lookup_days" '
                'in the "body" field of the response request'
            )
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        email_account = payload["email_account"]
        email_filter = payload["email_filter"]
        lookup_days = payload["lookup_days"]

        self._logger.info(
            f"Attempting to get all unread messages from email account {email_account} from the past {lookup_days} "
            f"days coming from {email_filter}"
        )

        unread_messages_response = await self._email_reader_repository.get_unread_emails(
            email_account,
            email_filter,
            lookup_days,
        )
        response["body"] = unread_messages_response["body"]
        response["status"] = unread_messages_response["status"]

        self._logger.info(f"Received the following from the gmail account {email_account}: " f'{response["body"]}')
        await self._event_bus.publish_message(msg["response_topic"], response)
