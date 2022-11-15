import json
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@pytest.fixture(scope="function")
def notifications_repository_instance():
    return NotificationsRepository(nats_client=Mock(), config=testconfig)


class TestNotificationsRepository:
    def instance_test(self):
        config = testconfig
        nats_client = Mock()

        notifications_repository = NotificationsRepository(nats_client, config)

        assert notifications_repository._config is config
        assert notifications_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository_instance):
        message = "Some message"

        notifications_repository_instance._nats_client.publish = AsyncMock()

        with uuid_mock:
            await notifications_repository_instance.send_slack_message(message)

        notifications_repository_instance._nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"[{notifications_repository_instance._config.LOG_CONFIG['name']}]: {message}"},
                }
            ),
        )
