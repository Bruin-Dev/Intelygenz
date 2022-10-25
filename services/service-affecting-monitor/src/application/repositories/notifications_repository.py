import json
from typing import Any

from shortuuid import uuid

from application import AffectingTroubles


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class NotificationsRepository:
    def __init__(self, nats_client, config):
        self._nats_client = nats_client
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f'[{self._config.LOG_CONFIG["name"]}] {message}'},
        }
        await self._nats_client.request("notification.slack.request", to_json_bytes(message), timeout=10)

    async def notify_successful_ticket_creation(self, ticket_id: int, serial_number: str, trouble: AffectingTroubles):
        message = (
            f"Service Affecting ticket has been created for serial number {serial_number}. Detected trouble was "
            f"{trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_successful_reopen(self, ticket_id: int, serial_number: str, trouble: AffectingTroubles):
        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been unresolved. "
            f"Detected trouble was {trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_successful_autoresolve(self, ticket_id: int, serial_number: str):
        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been autoresolved. "
            f"Details at https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_successful_ticket_forward(self, ticket_id: int, serial_number: str):
        message = (
            f"Task for serial number {serial_number} of Service Affecting ticket {ticket_id} has been forwarded to "
            "the HNOC queue"
        )
        await self.send_slack_message(message)

    async def notify_successful_note_append(self, ticket_id: int, serial_number: str, trouble: AffectingTroubles):
        message = (
            f"Service Affecting trouble note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"Detected trouble was {trouble.value.upper()}. https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_successful_reminder_note_append(self, ticket_id: int, serial_number: str):
        message = (
            f"Service Affecting reminder note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)
