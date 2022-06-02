from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application.repositories import nats_error_response
from application.repositories import t7_repository as t7_repository_module
from application.repositories.t7_repository import T7Repository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(t7_repository_module, "uuid", return_value=uuid_)


class TestT7Repository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        assert t7_repository._event_bus is event_bus
        assert t7_repository._logger is logger
        assert t7_repository._config is config
        assert t7_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_closed_tickets_test(self):
        ticket_id = 12345

        ticket_row = [
            {
                "Asset": "VCO123",
                "Notes": "Some notes",
                "EnteredDate_N": "2020-05-01T06:00:27.743-04:00",
                "Task Result": "Closed",
            }
        ]

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id, "ticket_rows": ticket_row},
        }
        response = {
            "request_id": uuid_,
            "body": "Success",
            "status": 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.post_metrics(ticket_id, ticket_row)

        event_bus.rpc_request.assert_awaited_once_with("t7.automation.metrics", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_closed_tickets_with_rpc_request_failing_test(self):
        ticket_id = 12345

        ticket_row = [
            {
                "Asset": "VCO123",
                "Notes": "Some notes",
                "EnteredDate_N": "2020-05-01T06:00:27.743-04:00",
                "Task Result": "Closed",
            }
        ]

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id, "ticket_rows": ticket_row},
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.post_metrics(ticket_id, ticket_row)

        event_bus.rpc_request.assert_awaited_once_with("t7.automation.metrics", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_closed_tickets_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345

        ticket_row = [
            {
                "Asset": "VCO123",
                "Notes": "Some notes",
                "EnteredDate_N": "2020-05-01T06:00:27.743-04:00",
                "Task Result": "Closed",
            }
        ]

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id, "ticket_rows": ticket_row},
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

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await t7_repository.post_metrics(ticket_id, ticket_row)

        event_bus.rpc_request.assert_awaited_once_with("t7.automation.metrics", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    def tnba_note_in_task_history_return_true_test(self):
        task_history = [
            {
                "ClientName": "Le Duff Management ",
                "Ticket Entered Date": "202008242225",
                "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                "CallTicketID": 4774915,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5180688,
                "Product": "SD-WAN",
                "Asset": "VC05200030905",
                "Address1": "1320 W Campbell Rd",
                "Address2": None,
                "City": "Richardson",
                "State": "TX",
                "Zip": "75080-2814",
                "Site Name": "01106 Coit Campbell",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\nAI\n\n",
                "Note Entered Date": "202008251726",
                "EnteredDate_N": "2020-08-25T17:26:00.583-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Resolved",
            }
        ]
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)
        tnba_exists = t7_repository.tnba_note_in_task_history(task_history)
        assert tnba_exists is True

    def tnba_note_in_task_history_return_false_test(self):
        task_history = [
            {
                "ClientName": "Le Duff Management ",
                "Ticket Entered Date": "202008242225",
                "EnteredDate": "2020-08-24T22:25:09.953-04:00",
                "CallTicketID": 4774915,
                "Initial Note @ Ticket Creation": "MetTel's IPA -- Service Outage Trouble",
                "DetailID": 5180688,
                "Product": "SD-WAN",
                "Asset": "VC05200030905",
                "Address1": "1320 W Campbell Rd",
                "Address2": None,
                "City": "Richardson",
                "State": "TX",
                "Zip": "75080-2814",
                "Site Name": "01106 Coit Campbell",
                "NoteType": "ADN",
                "Notes": "#*MetTel's IPA*#\n",
                "Note Entered Date": "202008251726",
                "EnteredDate_N": "2020-08-25T17:26:00.583-04:00",
                "Note Entered By": "Intelygenz Ai",
                "Task Assigned To": None,
                "Task": None,
                "Task Result": None,
                "SLA": 1,
                "Ticket Status": "Resolved",
            }
        ]
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        t7_repository = T7Repository(event_bus, logger, config, notifications_repository)
        tnba_exists = t7_repository.tnba_note_in_task_history(task_history)
        assert tnba_exists is False
