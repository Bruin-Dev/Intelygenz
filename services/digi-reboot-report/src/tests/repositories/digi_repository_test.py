from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from application.repositories import digi_repository as digi_repository_module
from application.repositories import nats_error_response
from application.repositories.digi_repository import DiGiRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(digi_repository_module, "uuid", return_value=uuid_)


class TestDiGiRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        assert digi_repository._event_bus is event_bus
        assert digi_repository._logger is logger
        assert digi_repository._config is config
        assert digi_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

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

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository.get_digi_recovery_logs()

        event_bus.rpc_request.assert_awaited_once_with("get.digi.recovery.logs", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_rpc_request_failing_test(self):
        logger = Mock()
        logger.error = Mock()
        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

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

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository.get_digi_recovery_logs()

        event_bus.rpc_request.assert_awaited_once_with("get.digi.recovery.logs", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_non_2xx_status_test(self):
        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        datetime_now = datetime.now()

        start_date_time = datetime_now - timedelta(days=config.DIGI_CONFIG["days_of_digi_recovery_log"])
        request = {"request_id": uuid_, "body": {"start_date_time": start_date_time, "size": "999"}}
        response = {"request_id": uuid_, "body": "ERROR", "status": 500}

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        digi_repository = DiGiRepository(event_bus, logger, config, notifications_repository)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime_now)
        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with uuid_mock:
                result = await digi_repository.get_digi_recovery_logs()

        event_bus.rpc_request.assert_awaited_once_with("get.digi.recovery.logs", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
