from unittest.mock import patch

import pytest
from application.repositories import email_repository as email_repository_module
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, email_repository, event_bus):
        assert email_repository._event_bus is event_bus
        assert email_repository._config is testconfig

    @pytest.mark.asyncio
    async def send_email_test(self, email_repository):
        email_data = {
            "request_id": uuid(),
            "email_data": {
                "subject": "some-subject",
                "recipient": "some-recipient",
                "text": "this is the accessible text for the email",
                "html": "<html><head>some-data</head><body>some-more-data</body></html>",
                "images": [],
                "attachments": [],
            },
        }

        await email_repository.send_email(email_data)

        email_repository._event_bus.rpc_request.assert_awaited_once_with(
            "notification.email.request", email_data, timeout=60
        )
