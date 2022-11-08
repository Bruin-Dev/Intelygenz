from unittest.mock import AsyncMock, Mock, patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig

        notifications_repository = NotificationsRepository(nats_client, config)

        assert notifications_repository._nats_client is nats_client
        assert notifications_repository._config is config

    @pytest.mark.asyncio
    async def send_slack_message_test(self):
        message = "Some message"

        nats_client = Mock()
        nats_client.publish = AsyncMock()
        config = testconfig

        notifications_repository = NotificationsRepository(nats_client, config)

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"[{notifications_repository._config.LOG_CONFIG['name']}] {message}"},
                }
            ),
        )