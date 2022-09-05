from dataclasses import dataclass

from framework.nats.client import Client
from shortuuid import uuid

from application.repositories.utils import to_json_bytes


@dataclass
class NotificationsRepository:
    _event_bus: Client

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "message": f"[email-tagger-monitor] {message}",
        }
        await self._event_bus.request("notification.slack.request", to_json_bytes(message), timeout=10)
