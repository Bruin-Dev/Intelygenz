from unittest.mock import AsyncMock, Mock, patch

import pytest
from shortuuid import uuid

from application.repositories import email_tagger_repository as email_tagger_repository_module
from application.repositories.email_tagger_repository import EmailTaggerRepository
from application.repositories.utils import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(email_tagger_repository_module, "uuid", return_value=uuid_)


class TestEmailTaggerRepository:
    def instance_test(self):
        event_bus = Mock()
        config = testconfig
        notifications_repository = Mock()

        email_tagger_repository = EmailTaggerRepository(event_bus, config, notifications_repository)

        assert email_tagger_repository._event_bus is event_bus
        assert email_tagger_repository._config is config
        assert email_tagger_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_prediction_ok_test(self, make_msg):
        config = testconfig
        notifications_repository = Mock()

        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            }
        }
        request = {"request_id": uuid_, "body": email_data}
        response = {
            "request_id": uuid_,
            "body": None,
            "status": 200,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        email_repository = EmailTaggerRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await email_repository.get_prediction(email_data)

        event_bus.request.assert_awaited_once_with(
            "email_tagger.prediction.request",
            to_json_bytes(request),
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"],
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_prediction_not_2XX_test(self, make_msg):
        config = testconfig

        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            }
        }
        response = {
            "request_id": uuid_,
            "body": "Fail",
            "status": 400,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = EmailTaggerRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_prediction(email_data)

        notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def save_metrics_ok_test(self, make_msg):
        config = testconfig
        notifications_repository = Mock()

        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            },
        }
        ticket_data = {"ticket_id": "123456"}
        request = {"request_id": uuid_, "body": {"original_email": email_data, "ticket": ticket_data}}
        response = {
            "request_id": uuid_,
            "body": None,
            "status": 200,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        email_repository = EmailTaggerRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await email_repository.save_metrics(email_data, ticket_data)

        event_bus.request.assert_awaited_once_with(
            "email_tagger.metrics.request",
            to_json_bytes(request),
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["kre_seconds"],
        )
        assert result == response
