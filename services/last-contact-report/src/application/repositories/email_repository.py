import logging

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class EmailRepository:
    def __init__(self, nats_client):
        self._nats_client = nats_client

    async def send_email(self, email_object: dict):
        await self._nats_client.request("notification.email.request", to_json_bytes(email_object), timeout=60)
