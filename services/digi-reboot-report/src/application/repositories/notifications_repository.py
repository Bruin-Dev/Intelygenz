import json
from typing import Any

from shortuuid import uuid


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class NotificationsRepository:
    def __init__(self, nats_client, config):
        self._nats_client = nats_client
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f"[{self._config.LOG_CONFIG['name']}]: {message}"},
        }
        await self._nats_client.publish("notification.slack.request", to_json_bytes(message))
