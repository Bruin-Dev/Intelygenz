from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        assert bruin_repository._nats_client is nats_client
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_closed_tickets_test(self):
        bruin_client_id = 12345
        ticket_topic = "VAS"

        next_run_time = datetime.now()

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "product_category": testconfig.PRODUCT_CATEGORY,
                "ticket_topic": ticket_topic,
                "ticket_statuses": ["Closed"],
                "start_date": (next_run_time - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": next_run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111},
                {"ticketID": 22222},
            ],
            "status": 200,
        }

        config = testconfig
        notifications_repository = Mock()

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await bruin_repository.get_closed_tickets(bruin_client_id, ticket_topic)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", to_json_bytes(request), timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_closed_tickets_with_request_failing_test(self):
        bruin_client_id = 12345
        ticket_topic = "VAS"

        next_run_time = datetime.now()

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "product_category": testconfig.PRODUCT_CATEGORY,
                "ticket_topic": ticket_topic,
                "ticket_statuses": ["Closed"],
                "start_date": (next_run_time - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": next_run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }

        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await bruin_repository.get_closed_tickets(bruin_client_id, ticket_topic)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", to_json_bytes(request), timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_closed_tickets_with_request_returning_non_2xx_status_test(self):
        bruin_client_id = 12345
        ticket_topic = "VAS"

        next_run_time = datetime.now()

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "product_category": testconfig.PRODUCT_CATEGORY,
                "ticket_topic": ticket_topic,
                "ticket_statuses": ["Closed"],
                "start_date": (next_run_time - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": next_run_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }

        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        config = testconfig

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await bruin_repository.get_closed_tickets(bruin_client_id, ticket_topic)

        nats_client.request.assert_awaited_once_with("bruin.ticket.basic.request", to_json_bytes(request), timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_outage_tickets_test(self):
        bruin_client_id = 12345

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.get_closed_tickets = AsyncMock()

        await bruin_repository.get_outage_tickets(bruin_client_id)
        bruin_repository.get_closed_tickets.assert_awaited_with(bruin_client_id, "VOO")

    @pytest.mark.asyncio
    async def get_affecting_tickets_test(self):
        bruin_client_id = 12345

        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)
        bruin_repository.get_closed_tickets = AsyncMock()

        await bruin_repository.get_affecting_tickets(bruin_client_id)
        bruin_repository.get_closed_tickets.assert_awaited_with(bruin_client_id, "VAS")

    @pytest.mark.asyncio
    async def get_ticket_task_history_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id},
        }
        response = {
            "request_id": uuid_,
            "body": [
                {
                    "ClientName": "Le Duff Management ",
                    "Ticket Entered Date": "202008242225",
                    "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                    "CallTicketID": 4774915,
                    "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                    "DetailID": None,
                    "Product": None,
                    "Asset": None,
                    "Address1": "1320 W Campbell Rd",
                    "Address2": None,
                    "City": "Richardson",
                    "State": "TX",
                    "Zip": "75080-2814",
                    "Site Name": "01106 Coit Campbell",
                    "NoteType": "ADN",
                    "Notes": None,
                    "Note Entered Date": "202008242236",
                    "EnteredDate_N": "2020-08-24T22:36:21.343-04:00",
                    "Note Entered By": "Intelygenz Ai",
                    "Task Assigned To": None,
                    "Task": None,
                    "Task Result": None,
                    "SLA": None,
                    "Ticket Status": "Resolved",
                }
            ],
            "status": 200,
        }

        config = testconfig
        notifications_repository = Mock()

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=120
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_request_failing_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id},
        }
        config = testconfig

        nats_client = Mock()
        nats_client.request = AsyncMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=120
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result is nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_request_returning_non_2xx_status_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id},
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        config = testconfig

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        nats_client = Mock()
        nats_client.request = AsyncMock(return_value=response_msg)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = AsyncMock()

        bruin_repository = BruinRepository(nats_client, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=120
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
