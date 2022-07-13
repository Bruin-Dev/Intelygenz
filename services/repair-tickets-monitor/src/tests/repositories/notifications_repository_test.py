from unittest.mock import patch

import pytest
from shortuuid import uuid

from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils import to_json_bytes

uuid_ = uuid()
uuid_patch = patch("application.repositories.notifications_repository.uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, event_bus):
        notifications_repository = NotificationsRepository(event_bus)

        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self, event_bus, notifications_repository):
        message = "Some message"

        with uuid_patch:
            await notifications_repository.send_slack_message(message)

        event_bus.request.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "message": f"[repair-tickets-monitor] {message}",
                }
            ),
            timeout=10,
        )
