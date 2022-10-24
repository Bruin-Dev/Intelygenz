import logging

from shortuuid import uuid

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class NotificationsRepository:
    def __init__(self, nats_client, config):
        self._nats_client = nats_client
        self._config = config

    async def send_slack_message(self, message: str):
        message = {
            "request_id": uuid(),
            "body": {"message": f"[{self._config.LOG_CONFIG['name']}] {message}"},
        }
        await self._nats_client.request("notification.slack.request", to_json_bytes(message), timeout=10)

    async def notify_successful_ticket_creation(self, ticket_id: int, service_number: str):
        await self.send_slack_message(
            f"Fraud ticket has been created for service number {service_number}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )

    async def notify_successful_reopen(self, ticket_id: int, service_number: str):
        await self.send_slack_message(
            f"Task for service number {service_number} of Fraud ticket {ticket_id} has been unresolved. "
            f"https://app.bruin.com/t/{ticket_id}"
        )

    async def notify_successful_ticket_forward(self, ticket_id: int, service_number: str):
        await self.send_slack_message(
            f"Task for service number {service_number} of Fraud ticket {ticket_id} has been forwarded to the HNOC queue"
        )

    async def notify_successful_note_append(self, ticket_id: int, service_number: str):
        await self.send_slack_message(
            f"Fraud note posted for service number {service_number} of ticket {ticket_id}. "
            f"https://app.bruin.com/t/{ticket_id}"
        )
