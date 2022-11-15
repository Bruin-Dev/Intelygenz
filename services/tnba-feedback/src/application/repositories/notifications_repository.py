from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, nats_client):
        self._nats_client = nats_client

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": message},
        }
        await self._nats_client.publish("notification.slack.request", to_json_bytes(message))
