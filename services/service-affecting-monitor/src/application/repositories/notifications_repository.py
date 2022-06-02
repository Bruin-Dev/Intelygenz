from application import AffectingTroubles
from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus, config):
        self._event_bus = event_bus
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "message": f'[{self._config.LOG_CONFIG["name"]}] {message}',
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def send_email(self, email_object: dict):
        await self._event_bus.rpc_request("notification.email.request", email_object, timeout=60)

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
