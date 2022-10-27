import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, nats_client):
        assert notifications_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository):
        message = "Some message"

        notifications_repository._nats_client.publish = AsyncMock()

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        notifications_repository._nats_client.publish.assert_awaited_once_with(
            "notification.slack.request",
            to_json_bytes(
                {
                    "request_id": uuid_,
                    "body": {"message": f"{message}"},
                }
            ),
        )
