from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from application.repositories import email_repository as email_repository_module
from application.repositories.email_repository import EmailRepository
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, event_bus):
        email_repository = EmailRepository(event_bus)

        assert email_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_email_test(self, event_bus):
        event_bus.rpc_request = CoroutineMock()
        email_repository = EmailRepository(event_bus)
        email_data = {
            "request_id": uuid(),
            "body": {
                "email_data": {
                    "subject": "some-subject",
                    "recipient": "some-recipient",
                    "text": "this is the accessible text for the email",
                    "html": "<html><head>some-data</head><body>some-more-data</body></html>",
                    "images": [],
                    "attachments": [],
                }
            },
        }

        await email_repository.send_email(email_data)

        email_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.email.request", email_data, timeout=60
        )
