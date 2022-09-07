from shortuuid import uuid


class NotificationsRepository:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": message},
        }
        await self._event_bus.rpc_request("notification.slack.request", message, timeout=10)

    async def notify_successful_reminder_note_append(self, ticket_id: int, serial_number: str):
        message = (
            f"Service Outage reminder note posted for serial number {serial_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)
