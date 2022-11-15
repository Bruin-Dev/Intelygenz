from dataclasses import dataclass

from application.repositories.utils import to_json_bytes
from framework.nats.client import Client
from shortuuid import uuid


@dataclass
class NotificationsRepository:
    _event_bus: Client

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f"[email-tagger-monitor] {message}"},
        }
        await self._event_bus.publish("notification.slack.request", to_json_bytes(message))
