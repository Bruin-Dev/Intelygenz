from unittest.mock import AsyncMock, patch

import pytest
from application.repositories import email_repository as email_repository_module
from application.repositories.email_repository import EmailRepository
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


class TestEmailRepository:
    def instance_test(self, nats_client):
        email_repository = EmailRepository(nats_client)

        assert email_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def send_email_test(self, nats_client):
        nats_client.publish = AsyncMock()
        email_repository = EmailRepository(nats_client)
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

        email_repository._nats_client.publish.assert_awaited_once_with(
            "notification.email.request", to_json_bytes(email_data)
        )
