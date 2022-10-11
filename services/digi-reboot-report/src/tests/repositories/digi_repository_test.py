import json
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import digi_repository as digi_repository_module
from application.repositories import nats_error_response
from application.repositories.digi_repository import DiGiRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(digi_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


@pytest.fixture(scope="function")
def digi_repository_instance():
    return DiGiRepository(nats_client=Mock(), config=testconfig, notifications_repository=Mock())


class TestDiGiRepository:
    def instance_test(self):
        config = testconfig
        notifications_repository = Mock()
        nats_client = Mock()
        digi_repository = DiGiRepository(nats_client, config, notifications_repository)

        assert digi_repository._config is config
        assert digi_repository._notifications_repository is notifications_repository
        assert digi_repository._nats_client is nats_client

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self, digi_repository_instance):
        config = testconfig

        datetime_now = datetime.now()

        start_date_time = datetime_now - timedelta(days=config.DIGI_CONFIG["days_of_digi_recovery_log"])
        request = {"request_id": uuid_, "body": {"start_date_time": start_date_time, "size": "999"}}
        response = {
            "request_id": uuid_,
            "body": {
                "Logs": [
                    {
                        "Id": 142,
                        "igzID": "42",
                        "RequestID": "959b1e34-2b10-4e04-967e-7ac268d2cb1b",
                        "Method": "API Start",
                        "System": "NYD",
                        "VeloSerial": "VC00000613",
                        "TicketID": "3569284",
                        "DeviceSN": "NYD",
                        "Notes": "API Called 02/15/2021 11:08:26",
                        "TimestampSTART": "2021-02-15T16:08:26Z",
                        "TimestampEND": "2021-02-15T16:08:28Z",
                    }
                ]
            },
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        digi_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository_instance.get_digi_recovery_logs()

        digi_repository_instance._nats_client.request.assert_awaited_once_with(
            "get.digi.recovery.logs", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_rpc_request_failing_test(self, digi_repository_instance):
        digi_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        datetime_now = datetime.now()

        start_date_time = datetime_now - timedelta(
            days=digi_repository_instance._config.DIGI_CONFIG["days_of_digi_recovery_log"]
        )
        request = {"request_id": uuid_, "body": {"start_date_time": start_date_time, "size": "999"}}

        digi_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository_instance.get_digi_recovery_logs()

        digi_repository_instance._nats_client.request.assert_awaited_once_with(
            "get.digi.recovery.logs", to_json_bytes(request), timeout=90
        )
        digi_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_non_2xx_status_test(self, digi_repository_instance):

        digi_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        datetime_now = datetime.now()

        start_date_time = datetime_now - timedelta(
            days=digi_repository_instance._config.DIGI_CONFIG["days_of_digi_recovery_log"]
        )
        request = {"request_id": uuid_, "body": {"start_date_time": start_date_time, "size": "999"}}
        response = {"request_id": uuid_, "body": "ERROR", "status": 500}
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        digi_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository_instance.get_digi_recovery_logs()

        digi_repository_instance._nats_client.request.assert_awaited_once_with(
            "get.digi.recovery.logs", to_json_bytes(request), timeout=90
        )
        digi_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
