import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    @staticmethod
    def to_json_bytes(message: dict[str, Any]):
        return json.dumps(message, default=str, separators=(",", ":")).encode()

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"
        notifications_repository._nats_client.publish = AsyncMock()

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            self.to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"[{notifications_repository._config.LOG_CONFIG['name']}]: {message}"},
                }
            ),
        )
