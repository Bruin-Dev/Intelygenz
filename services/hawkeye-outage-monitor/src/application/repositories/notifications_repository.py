import json
from typing import Any

from shortuuid import uuid


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class NotificationsRepository:
    def __init__(self, nats_client):
        self._nats_client = nats_client

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": message},
        }
        await self._nats_client.request("notification.slack.request", to_json_bytes(message), timeout=10)
