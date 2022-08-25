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
            "message": f"[{self._config.LOG_CONFIG['name']}]: {message}",
        }
        await self._nats_client.request("notification.slack.request", to_json_bytes(message), timeout=10)
