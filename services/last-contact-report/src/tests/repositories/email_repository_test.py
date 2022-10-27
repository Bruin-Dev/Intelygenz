from unittest.mock import AsyncMock, Mock, patch

import pytest
from shortuuid import uuid

from application.repositories import email_repository as email_repository_module
from application.repositories.email_repository import EmailRepository
from application.repositories.utils_repository import to_json_bytes

uuid_ = uuid()
uuid_mock = patch.object(email_repository_module, "uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def mock_nats_client():
    nats_client = Mock()
    nats_client.publish = AsyncMock()
    return nats_client


@pytest.fixture(scope="function")
def instance_email_repository(mock_nats_client):
    return EmailRepository(mock_nats_client)


class TestEmailRepository:
    def instance_test(self, instance_email_repository, mock_nats_client):
        assert instance_email_repository._nats_client is mock_nats_client

    @pytest.mark.asyncio
    async def send_email_test(self, instance_email_repository):
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

        await instance_email_repository.send_email(email_data)

        instance_email_repository._nats_client.publish.assert_awaited_once_with(
            "notification.email.request", to_json_bytes(email_data)
        )
