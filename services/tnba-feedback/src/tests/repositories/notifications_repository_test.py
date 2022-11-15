from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self):
        nats_client = Mock()

        notifications_repository = NotificationsRepository(nats_client)

        assert notifications_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def send_slack_message_test(self):
        message = "Some message"

        nats_client = Mock()
        nats_client.publish = AsyncMock()

        notifications_repository = NotificationsRepository(nats_client)

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": message},
                }
            ),
        )
