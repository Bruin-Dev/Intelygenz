import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import digi_repository as digi_repository_module
from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(digi_repository_module, "uuid", return_value=uuid_)


class TestDiGiRepository:
    def instance_test(self, digi_repository, nats_client, notifications_repository):
        assert digi_repository._nats_client is nats_client
        assert digi_repository._config is testconfig
        assert digi_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def reboot_link_success_test(self, digi_repository):
        ticket_id = 11111
        service_number = "VC1234567"
        logical_id = "00:04:2d:123"
        request = {
            "request_id": uuid_,
            "body": {"velo_serial": service_number, "ticket": str(ticket_id), "MAC": logical_id},
        }
        return_body = {"body": "Success", "status": 200}

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(return_body)

        digi_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        digi_repository._nats_client.request.assert_awaited_once_with(
            "digi.reboot", to_json_bytes(request), timeout=150
        )
        assert result == return_body

    @pytest.mark.asyncio
    async def reboot_link_success_with_request_failing_test(self, digi_repository):
        ticket_id = 11111
        service_number = "VC1234567"
        logical_id = "00:04:2d:123"
        request = {
            "request_id": uuid_,
            "body": {"velo_serial": service_number, "ticket": str(ticket_id), "MAC": logical_id},
        }
        digi_repository._nats_client.request = AsyncMock(side_effect=Exception)
        digi_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        digi_repository._nats_client.request.assert_awaited_once_with(
            "digi.reboot", to_json_bytes(request), timeout=150
        )
        digi_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def reboot_link_success_with_non_2xx_status_test(self, digi_repository):
        ticket_id = 11111
        service_number = "VC1234567"
        logical_id = "00:04:2d:123"
        request = {
            "request_id": uuid_,
            "body": {"velo_serial": service_number, "ticket": str(ticket_id), "MAC": logical_id},
        }
        return_body = {"body": "Failed", "status": 400}

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(return_body)

        digi_repository._nats_client.request = AsyncMock(return_value=response_msg)
        digi_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await digi_repository.reboot_link(service_number, ticket_id, logical_id)

        digi_repository._nats_client.request.assert_awaited_once_with(
            "digi.reboot", to_json_bytes(request), timeout=150
        )
        digi_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == return_body

    def get_digi_links_test(self, digi_repository):
        logical_id_list = [
            {"interface_name": "test", "logical_id": "123"},
            {"interface_name": "GE1", "logical_id": "00:27:04:123"},
            {"interface_name": "GE3", "logical_id": "00:27:04:122"},
            {"interface_name": "GE2", "logical_id": "00:04:2d:123"},
        ]
        expected_digi_list = [logical_id_list[1], logical_id_list[2], logical_id_list[3]]

        digi_links = digi_repository.get_digi_links(logical_id_list)

        assert digi_links == expected_digi_list

    def is_digi_link_test(self, digi_repository):
        link_1 = {"interface_name": "GE1", "logical_id": "00:27:04:122"}
        link_2 = {"interface_name": "GE2", "logical_id": "00:00:00:000"}

        assert digi_repository.is_digi_link(link_1) is True
        assert digi_repository.is_digi_link(link_2) is False

    def get_interface_name_from_digi_note_test(self, digi_repository):
        expected_interface = "GE2"
        digi_reboot_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Offline DiGi interface identified for serial: VCO",
                f"Interface: {expected_interface}",
                f"Automatic reboot attempt started.",
                f"TimeStamp: ",
            ]
        )
        bruin_note = {"noteValue": digi_reboot_note}

        interface = digi_repository.get_interface_name_from_digi_note(bruin_note)

        assert interface == expected_interface

    def get_interface_name_from_digi_note_no_interface_test(self, digi_repository):
        digi_reboot_note = os.linesep.join(
            [
                f"#*MetTel's IPA*#",
                f"Offline DiGi interface identified for serial: VCO",
                f"Automatic reboot attempt started.",
                f"TimeStamp: ",
            ]
        )
        bruin_note = {"noteValue": digi_reboot_note}

        interface = digi_repository.get_interface_name_from_digi_note(bruin_note)

        assert interface == ""

    def get_interface_name_from_digi_note_no_note_value_test(self, digi_repository):
        bruin_note = {}

        interface = digi_repository.get_interface_name_from_digi_note(bruin_note)

        assert interface == ""
