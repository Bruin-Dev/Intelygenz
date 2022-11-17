from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils import to_json_bytes
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self):
        event_bus = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, config, notifications_repository)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def post_email_tag_ok_test(self, make_msg):
        config = testconfig
        notifications_repository = Mock()

        email_id = "12345"
        prediction = [
            {"tag_id": "1004", "probability": 0.6},
            {"tag_id": "1001", "probability": 0.3},
            {"tag_id": "1002", "probability": 0.1},
        ]
        tag_id = "1004"
        request = {
            "request_id": uuid_,
            "body": {
                "email_id": email_id,
                "tag_id": tag_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": None,
            "status": 200,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        bruin_repository = BruinRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.post_email_tag(email_id, prediction[0]["tag_id"])

        event_bus.request.assert_awaited_once_with(
            "bruin.email.tag.request",
            to_json_bytes(request),
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["post_email_tag_seconds"],
        )
        assert result == response

    @pytest.mark.asyncio
    async def post_email_tag_not_2XX_test(self, make_msg):
        config = testconfig

        email_id = "12345"
        prediction = [
            {"tag_id": "1004", "probability": 0.6},
            {"tag_id": "1001", "probability": 0.3},
            {"tag_id": "1002", "probability": 0.1},
        ]
        response = {
            "request_id": uuid_,
            "body": "Fail",
            "status": 400,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.post_email_tag(email_id, prediction[0]["tag_id"])

        notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def get_single_ticket_basic_info_ok_test(self, make_msg):
        config = testconfig
        notifications_repository = Mock()

        ticket_id = "5678"
        ticket_detail_response = {
            "ticketID": "5678",
            "ticketStatus": "Closed",
            "callType": "BIL",
            "category": "010",
            "createDate": "2021-01-01T10:00:00.000",
        }
        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": ticket_detail_response,
            "status": 200,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        bruin_repository = BruinRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        event_bus.request.assert_awaited_once_with(
            "bruin.single_ticket.basic.request",
            to_json_bytes(request),
            timeout=config.MONITOR_CONFIG["nats_request_timeout"]["post_email_tag_seconds"],
        )

        assert result == {
            "request_id": uuid_,
            "body": {
                "ticket_id": "5678",
                "ticket_status": "Closed",
                "call_type": "BIL",
                "category": "010",
                "creation_date": "2021-01-01T10:00:00.000",
            },
            "status": 200,
        }

    @pytest.mark.asyncio
    async def get_single_ticket_basic_info_not_2XX_test(self, make_msg):
        config = testconfig

        ticket_id = "5678"
        response = {
            "request_id": uuid_,
            "body": "Fail",
            "status": 400,
        }
        event_bus = Mock()
        event_bus.request = AsyncMock(return_value=make_msg(response))

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(event_bus, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_single_ticket_basic_info(ticket_id)

        notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response
