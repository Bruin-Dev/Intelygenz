from shortuuid import uuid

from application.repositories.utils_repository import to_json_bytes


class NotificationsRepository:
    def __init__(self, nats_client):
        self._nats_client = nats_client

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": message},
        }
        await self._nats_client.request("notification.slack.request", to_json_bytes(message), timeout=10)
