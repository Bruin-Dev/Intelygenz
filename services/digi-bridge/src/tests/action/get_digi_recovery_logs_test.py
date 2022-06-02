from unittest.mock import Mock

import pytest
from application.actions.get_digi_recovery_logs import DiGiRecoveryLogs
from asynctest import CoroutineMock


class TestDiGiRecoveryLogs:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        digi_repository = Mock()

        digi_recovery_logs = DiGiRecoveryLogs(logger, event_bus, digi_repository)

        assert digi_recovery_logs._logger == logger
        assert digi_recovery_logs._event_bus == event_bus
        assert digi_recovery_logs._digi_repository == digi_repository

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        igz_id = "test_id"
        payload = {"igzID": igz_id}

        msg = {"request_id": "123", "response_topic": "231", "body": {**payload}}

        digi_recovery_logs_return = {
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
                        "Notes": "Notes",
                        "TimestampSTART": "2021-02-15T16:08:26Z",
                        "TimestampEND": "2021-02-15T16:08:28Z",
                    }
                ],
                "Count": 10,
                "Size": "50",
                "Offset": "0",
            },
            "status": 200,
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = CoroutineMock(return_value=digi_recovery_logs_return)

        digi_recovery_logs = DiGiRecoveryLogs(logger, event_bus, digi_repository)

        await digi_recovery_logs.get_digi_recovery_logs(msg)

        digi_repository.get_digi_recovery_logs.assert_awaited_once_with(payload)
        event_bus.publish_message.assert_awaited_once_with(
            msg["response_topic"],
            dict(
                request_id=msg["request_id"],
                body=digi_recovery_logs_return["body"],
                status=digi_recovery_logs_return["status"],
            ),
        )

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_no_body_test(self):
        igz_id = "test_id"
        payload = {"igzID": igz_id}

        msg = {
            "request_id": "123",
            "response_topic": "231",
        }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = CoroutineMock()

        digi_recovery_logs = DiGiRecoveryLogs(logger, event_bus, digi_repository)

        await digi_recovery_logs.get_digi_recovery_logs(msg)

        digi_repository.get_digi_recovery_logs.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with(
            msg["response_topic"], dict(request_id=msg["request_id"], body='Must include "body" in request', status=400)
        )
