from application.repositories.utils import to_json_bytes
from dataclasses import dataclass
from framework.nats.client import Client as NatsClient
from shortuuid import uuid


@dataclass
class NotificationsRepository:
    _event_bus: NatsClient

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f"[repair-tickets-monitor] {message}"},
        }

        await self._event_bus.request("notification.slack.request", to_json_bytes(message), timeout=10)
