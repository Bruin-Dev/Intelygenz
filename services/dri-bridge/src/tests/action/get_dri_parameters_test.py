from unittest.mock import Mock
from shortuuid import uuid
import pytest
from application.actions.get_dri_parameters import GetDRIParameters
from asynctest import CoroutineMock

_uuid = uuid()


class TestGetDRIParameters:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        dri_repository = Mock()

        get_dri_parameters = GetDRIParameters(logger, event_bus, dri_repository)

        assert get_dri_parameters._logger is logger
        assert get_dri_parameters._event_bus is event_bus
        assert get_dri_parameters._dri_repository is dri_repository

    @pytest.mark.asyncio
    async def get_dri_parameters_test(self):
        serial = 'VCO123'
        parameter_set = {
                            "ParameterNames": [
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress"
                            ],
                            "Source": 0
                            }
        task_status_response = {
            "body": {
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT"
            },
            "status": 200
        }

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock(return_value=task_status_response)

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        msg_body = {
            'serial_number': serial,
            'parameter_set': parameter_set
        }
        event_bus_request = {
            'request_id': _uuid,
            'body': msg_body,
            'response_topic': 'some_topic'
        }

        event_bus_respone = {
            'request_id': _uuid,
            **task_status_response
        }
        get_dri_parameters = GetDRIParameters(logger, event_bus, dri_repository)

        await get_dri_parameters.get_dri_parameters(event_bus_request)
        dri_repository.get_dri_parameters.assert_awaited_once_with(serial, parameter_set)
        event_bus.publish_message.assert_awaited_once_with('some_topic', event_bus_respone)

    @pytest.mark.asyncio
    async def get_dri_parameters_no_body_test(self):
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock()

        event_bus_request = {
            'request_id': _uuid,
            'response_topic': 'some_topic'
        }

        event_bus_respone = {
            'request_id': _uuid,
            'body': 'You must specify {.."body":{"serial_number", "parameter_set"}...} in the request',
            'status': 400
        }
        get_dri_parameters = GetDRIParameters(logger, event_bus, dri_repository)

        await get_dri_parameters.get_dri_parameters(event_bus_request)
        dri_repository.get_dri_parameters.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with('some_topic', event_bus_respone)

    @pytest.mark.asyncio
    async def get_dri_parameters_no_serial_test(self):
        parameter_set = {
                            "ParameterNames": [
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress"
                            ],
                            "Source": 0
                            }

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock()

        msg_body = {
            'parameter_set': parameter_set
        }

        event_bus_request = {
            'request_id': _uuid,
            'body': msg_body,
            'response_topic': 'some_topic'
        }

        event_bus_respone = {
            'request_id': _uuid,
            'body': 'You must specify "serial_number" and "parameter_set" in the body',
            'status': 400
        }
        get_dri_parameters = GetDRIParameters(logger, event_bus, dri_repository)

        await get_dri_parameters.get_dri_parameters(event_bus_request)
        dri_repository.get_dri_parameters.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with('some_topic', event_bus_respone)

    @pytest.mark.asyncio
    async def get_dri_parameters_no_parameter_set_test(self):
        serial = 'VCO123'

        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        dri_repository = Mock()
        dri_repository.get_dri_parameters = CoroutineMock()

        msg_body = {
            'serial_number': serial,
        }

        event_bus_request = {
            'request_id': _uuid,
            'body': msg_body,
            'response_topic': 'some_topic'
        }

        event_bus_respone = {
            'request_id': _uuid,
            'body': 'You must specify "serial_number" and "parameter_set" in the body',
            'status': 400
        }
        get_dri_parameters = GetDRIParameters(logger, event_bus, dri_repository)

        await get_dri_parameters.get_dri_parameters(event_bus_request)
        dri_repository.get_dri_parameters.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with('some_topic', event_bus_respone)
