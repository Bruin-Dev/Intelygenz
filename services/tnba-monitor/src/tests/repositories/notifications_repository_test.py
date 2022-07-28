from unittest.mock import patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, event_bus):
        assert notifications_repository._event_bus is event_bus
        assert notifications_repository._config is testconfig

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        prefix = testconfig.LOG_CONFIG["name"]
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                "request_id": uuid_,
                "message": f"[{prefix}] {message}",
            },
            timeout=10,
        )