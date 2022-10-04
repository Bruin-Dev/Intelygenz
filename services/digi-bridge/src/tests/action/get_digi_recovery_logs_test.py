import json
from unittest.mock import AsyncMock, Mock

import humps
import pytest
from nats.aio.msg import Msg

from application.actions.get_digi_recovery_logs import DiGiRecoveryLogs


class TestDiGiRecoveryLogs:
    def instance_test(self):
        digi_repository = Mock()

        digi_recovery_logs = DiGiRecoveryLogs(digi_repository)

        assert digi_recovery_logs._digi_repository == digi_repository

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        igz_id = "test_id"
        payload = {"igzID": igz_id}

        msg = {"request_id": "123", "response_topic": "231", "body": {**payload}}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()

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

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = AsyncMock(return_value=digi_recovery_logs_return)

        digi_recovery_logs = DiGiRecoveryLogs(digi_repository)

        await digi_recovery_logs(msg_mock)

        digi_repository.get_digi_recovery_logs.assert_awaited_once_with(humps.pascalize(payload))

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_no_body_test(self):
        igz_id = "test_id"

        msg = {
            "request_id": "123",
            "response_topic": "231",
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()

        digi_repository = Mock()
        digi_repository.get_digi_recovery_logs = AsyncMock()

        digi_recovery_logs = DiGiRecoveryLogs(digi_repository)

        await digi_recovery_logs(msg_mock)

        digi_repository.get_digi_recovery_logs.assert_not_awaited()
