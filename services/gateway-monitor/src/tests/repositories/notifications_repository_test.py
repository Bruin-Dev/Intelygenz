from unittest.mock import patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from asynctest import CoroutineMock
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, event_bus):
        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"

        notifications_repository._event_bus.rpc_request = CoroutineMock()

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                "request_id": uuid_,
                "body": {"message": f"{message}"},
            },
            timeout=10,
        )
