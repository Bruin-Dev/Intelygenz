from unittest.mock import AsyncMock, Mock, patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils import to_json_bytes

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self):
        event_bus = Mock()

        notifications_repository = NotificationsRepository(event_bus)

        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self):
        message = "Some message"

        event_bus = Mock()
        event_bus.request = AsyncMock()

        notifications_repository = NotificationsRepository(event_bus)

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        event_bus.request.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"[email-tagger-monitor] {message}"},
                }
            ),
            timeout=10,
        )
