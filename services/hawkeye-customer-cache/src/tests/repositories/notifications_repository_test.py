from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, 'uuid', return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self):
        event_bus = Mock()
        config = testconfig

        notifications_repository = NotificationsRepository(event_bus, config)

        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self):
        prefix = testconfig.LOG_CONFIG["name"]
        message = "Some message"

        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        notifications_repository = NotificationsRepository(event_bus, config)

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': f'[{prefix}] {message}',
            },
            timeout=10,
        )
