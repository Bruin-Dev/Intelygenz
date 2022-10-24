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

    async def notify_ticket_creation(self, ticket_id: int, serial_number: str):
        message = (
            f"Service Affecting ticket created for Ixia device {serial_number}: https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_ticket_detail_was_unresolved(self, ticket_id: int, serial_number: str):
        message = (
            f"Detail corresponding to Ixia device {serial_number} in Service Affecting ticket {ticket_id} has been "
            f"unresolved: https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)

    async def notify_multiple_notes_were_posted_to_ticket(self, ticket_id: int, serial_number: str):
        message = (
            f"Multiple Affecting notes related to Ixia device {serial_number} were posted to Service Affecting ticket "
            f"{ticket_id}: https://app.bruin.com/t/{ticket_id}"
        )
        await self.send_slack_message(message)
