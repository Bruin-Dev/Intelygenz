import json
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@pytest.fixture(scope="function")
def bruin_repository_instance():
    return BruinRepository(nats_client=Mock(), config=testconfig, notifications_repository=Mock())


class TestBruinRepository:
    def instance_test(self):
        config = testconfig
        notifications_repository = Mock()
        nats_client = Mock()

        bruin_repository = BruinRepository(
            config=config, notifications_repository=notifications_repository, nats_client=nats_client
        )

        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository
        assert bruin_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def get_ticket_task_history_test(self, bruin_repository_instance):
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
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_task_history(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=60
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {"ticket_id": ticket_id},
        }
        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_task_history(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=60
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result is nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
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

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_task_history(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", to_json_bytes(request), timeout=60
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
