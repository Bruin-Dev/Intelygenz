from unittest.mock import AsyncMock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, nats_client):
        assert notifications_repository._nats_client is nats_client
        assert notifications_repository._config is testconfig

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"

        request = {
            "request_id": uuid_,
            "message": f"[{notifications_repository._config.LOG_CONFIG['name']}]: {message}",
        }
        encoded_request = to_json_bytes(request)

        notifications_repository._nats_client.request = AsyncMock()

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.request.assert_awaited_once_with(
            "notification.slack.request",
            encoded_request,
            timeout=10,
        )
