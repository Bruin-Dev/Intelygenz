from unittest.mock import AsyncMock, patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"
        notifications_repository._nats_client.rpc_request = AsyncMock()

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                "request_id": uuid_,
                "body": {"message": f"[{notifications_repository._config.LOG_CONFIG['name']}]: {message}"},
            },
            timeout=10,
        )
