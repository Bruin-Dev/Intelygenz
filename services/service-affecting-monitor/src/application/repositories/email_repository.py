import json
from typing import Any


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class EmailRepository:
    def __init__(self, nats_client):
        self._nats_client = nats_client

    async def send_email(self, email_object: dict):
        await self._nats_client.publish("notification.email.request", to_json_bytes(email_object))
