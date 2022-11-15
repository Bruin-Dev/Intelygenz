import json
from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_dri_parameters import GetDRIParameters
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg
from shortuuid import uuid

_uuid = uuid()


class TestGetDRIParameters:
    def instance_test(self):
        dri_repository = Mock()

        get_dri_parameters = GetDRIParameters(dri_repository)

        assert get_dri_parameters._dri_repository is dri_repository

    @pytest.mark.asyncio
    async def get_dri_parameters_test(self):
        serial = "VCO123"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }
        task_status_response = {
            "body": {"InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT"},
            "status": 200,
        }

        dri_repository = Mock()
        dri_repository.get_dri_parameters = AsyncMock(return_value=task_status_response)

        msg_body = {"serial_number": serial, "parameter_set": parameter_set}
        event_bus_request = {"body": msg_body, "response_topic": "some_topic"}

        event_bus_respone = {**task_status_response}
        get_dri_parameters = GetDRIParameters(dri_repository)

        msg = Mock(spec_set=Msg)
        msg.data = json.dumps(event_bus_request).encode()

        await get_dri_parameters(msg)
        dri_repository.get_dri_parameters.assert_awaited_once_with(serial, parameter_set)
        msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_respone))

    @pytest.mark.asyncio
    async def get_dri_parameters_no_body_test(self):
        dri_repository = Mock()
        dri_repository.get_dri_parameters = AsyncMock()

        event_bus_request = {"response_topic": "some_topic"}

        event_bus_respone = {
            "body": 'You must specify {.."body":{"serial_number", "parameter_set"}...} in the request',
            "status": 400,
        }
        get_dri_parameters = GetDRIParameters(dri_repository)

        msg = Mock(spec_set=Msg)
        msg.data = json.dumps(event_bus_request).encode()

        await get_dri_parameters(msg)
        dri_repository.get_dri_parameters.assert_not_awaited()
        msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_respone))

    @pytest.mark.asyncio
    async def get_dri_parameters_no_serial_test(self):
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        dri_repository = Mock()
        dri_repository.get_dri_parameters = AsyncMock()

        msg_body = {"parameter_set": parameter_set}

        event_bus_request = {"body": msg_body, "response_topic": "some_topic"}

        event_bus_respone = {
            "body": 'You must specify "serial_number" and "parameter_set" in the body',
            "status": 400,
        }
        get_dri_parameters = GetDRIParameters(dri_repository)

        msg = Mock(spec_set=Msg)
        msg.data = json.dumps(event_bus_request).encode()

        await get_dri_parameters(msg)
        dri_repository.get_dri_parameters.assert_not_awaited()
        msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_respone))

    @pytest.mark.asyncio
    async def get_dri_parameters_no_parameter_set_test(self):
        serial = "VCO123"

        dri_repository = Mock()
        dri_repository.get_dri_parameters = AsyncMock()

        msg_body = {
            "serial_number": serial,
        }

        event_bus_request = {"body": msg_body, "response_topic": "some_topic"}

        event_bus_respone = {
            "body": 'You must specify "serial_number" and "parameter_set" in the body',
            "status": 400,
        }
        get_dri_parameters = GetDRIParameters(dri_repository)

        msg = Mock(spec_set=Msg)
        msg.data = json.dumps(event_bus_request).encode()

        await get_dri_parameters(msg)
        dri_repository.get_dri_parameters.assert_not_awaited()
        msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_respone))
