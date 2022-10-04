import json
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import humps
import pytest
from nats.aio.msg import Msg

from application.actions.digi_reboot import DiGiReboot


class TestDiGiReboot:
    def instance_test(self):
        digi_repository = Mock()

        digi_reboot = DiGiReboot(digi_repository)

        assert digi_reboot._digi_repository == digi_repository

    @pytest.mark.asyncio
    async def digi_reboot_test(self):
        body = {"velo_serial": "VC05200046188", "ticket": "3574667", "MAC": "00:04:2d:0b:cf:7f:0000"}
        msg = {
            "igzID": "123",
            "response_topic": "231",
            "body": {"velo_serial": "VC05200046188", "ticket": "3574667", "MAC": "00:04:2d:0b:cf:7f:0000"},
        }

        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()
        response_status = HTTPStatus.OK
        reboot_return = {"igzID": "123", "body": body, "status": response_status}

        digi_repository = Mock()
        digi_repository.reboot = AsyncMock(return_value=reboot_return)

        digi_reboot = DiGiReboot(digi_repository)

        await digi_reboot(msg_mock)

        digi_repository.reboot.assert_awaited_once_with(humps.pascalize(msg["body"]))

    @pytest.mark.asyncio
    async def digi_reboot_no_body_test(self):
        msg = {"request_id": "123", "response_topic": "231"}

        digi_repository = Mock()
        digi_repository.reboot = AsyncMock()

        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()
        digi_reboot = DiGiReboot(digi_repository)

        await digi_reboot(msg_mock)

        digi_repository.reboot.assert_not_awaited()

    @pytest.mark.asyncio
    async def digi_reboot_empty_body_test(self):
        msg = {"request_id": "123", "response_topic": "231", "body": {}}

        digi_repository = Mock()
        digi_repository.reboot = AsyncMock()

        digi_reboot = DiGiReboot(digi_repository)

        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()

        await digi_reboot(msg_mock)

        digi_repository.reboot.assert_not_awaited()

    @pytest.mark.asyncio
    async def digi_reboot_with_not_al_keys_in_body_test(self):
        body = {"velo_serial": "VC05200046188", "ticket": "3574667"}
        msg = {"request_id": "123", "response_topic": "231", "body": body}

        digi_repository = Mock()
        digi_repository.reboot = AsyncMock()

        digi_reboot = DiGiReboot(digi_repository)

        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(msg).encode()

        await digi_reboot(msg_mock)

        digi_repository.reboot.assert_not_awaited()
