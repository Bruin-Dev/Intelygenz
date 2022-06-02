from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

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

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.get.task.history", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_failing_test(self):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id},
        }
        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.get.task.history", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result is nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_returning_non_2xx_status_test(self):
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

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.get.task.history", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
