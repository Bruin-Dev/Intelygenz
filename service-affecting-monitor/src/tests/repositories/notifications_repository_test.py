from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.notifications_repository import NotificationsRepository


uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, 'uuid', return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self):
        event_bus = Mock()

        notifications_repository = NotificationsRepository(event_bus)

        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self):
        message = "Some message"

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        notifications_repository = NotificationsRepository(event_bus)

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                'request_id': uuid_,
                'message': message,
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def send_email_test(self):
        email_data = {
            'request_id': uuid(),
            'email_data': {
                'subject': 'some-subject',
                'recipient': 'some-recipient',
                'text': 'this is the accessible text for the email',
                'html': '<html><head>some-data</head><body>some-more-data</body></html>',
                'images': [],
                'attachments': []
            }
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock()

        notifications_repository = NotificationsRepository(event_bus)

        await notifications_repository.send_email(email_data)

        event_bus.rpc_request.assert_awaited_once_with("notification.email.request", email_data, timeout=60)

    @pytest.mark.asyncio
    async def notify_successful_ticket_forward_test(self):
        ticket_id = 12345
        serial_number = 'VC1234567'

        event_bus = Mock()

        notifications_repository = NotificationsRepository(event_bus)
        notifications_repository.send_slack_message = CoroutineMock()

        await notifications_repository.notify_successful_ticket_forward(
            ticket_id=ticket_id, serial_number=serial_number
        )

        message = (
            f'Detail related to serial {serial_number} in ticket {ticket_id} was successfully forwarded '
            'to the HNOC queue'
        )
        notifications_repository.send_slack_message.assert_awaited_once_with(message)
