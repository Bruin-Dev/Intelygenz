from unittest.mock import Mock, patch

import pytest
from application.repositories import dri_repository as dri_repository_module
from application.repositories import nats_error_response
from application.repositories.dri_repository import DRIRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(dri_repository_module, "uuid", return_value=uuid_)


class TestDRIRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        dri_repository = DRIRepository(event_bus, logger, config, notifications_repository)

        assert dri_repository._event_bus is event_bus
        assert dri_repository._logger is logger
        assert dri_repository._config is config
        assert dri_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_dri_parameters_test(self):
        serial = "70059"

        request = {
            "request_id": uuid_,
            "body": {
                "serial_number": serial,
                "parameter_set": {
                    "ParameterNames": [
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
                    ],
                    "Source": 0,
                },
            },
        }

        mac_add = "8C:19:2D:23:30:69"
        response = {
            "request_id": uuid_,
            "body": {
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei": "864839040023968",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid": "89014103272191198072",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert": "SIM1 Active",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum": "15245139487",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress": mac_add,
            },
            "status": 200,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        dri_repository = DRIRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await dri_repository.get_dri_parameters(serial)

        event_bus.rpc_request.assert_awaited_once_with("dri.parameters.request", request, timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_dri_parameters_rpc_request_failed_test(self):
        serial = "70059"

        request = {
            "request_id": uuid_,
            "body": {
                "serial_number": serial,
                "parameter_set": {
                    "ParameterNames": [
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
                    ],
                    "Source": 0,
                },
            },
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        dri_repository = DRIRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await dri_repository.get_dri_parameters(serial)

        event_bus.rpc_request.assert_awaited_once_with("dri.parameters.request", request, timeout=120)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_dri_parameters_non_2xx_test(self):
        serial = "70059"

        request = {
            "request_id": uuid_,
            "body": {
                "serial_number": serial,
                "parameter_set": {
                    "ParameterNames": [
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
                    ],
                    "Source": 0,
                },
            },
        }

        response = {
            "request_id": uuid_,
            "body": f"DRI task was rejected for serial {serial}",
            "status": 400,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        logger.error = Mock()

        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        dri_repository = DRIRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await dri_repository.get_dri_parameters(serial)

        event_bus.rpc_request.assert_awaited_once_with("dri.parameters.request", request, timeout=120)
        assert result == response

    @pytest.mark.asyncio
    async def get_dri_parameters_204_test(self):
        serial = "70059"

        request = {
            "request_id": uuid_,
            "body": {
                "serial_number": serial,
                "parameter_set": {
                    "ParameterNames": [
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                        "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                        "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
                    ],
                    "Source": 0,
                },
            },
        }

        msg = f"Data is still being fetched from DRI for serial {serial}"
        err_msg = f"Max retries reached when getting dri parameters - exception: Error: {msg}"

        response = {
            "request_id": uuid_,
            "body": msg,
            "status": 204,
        }

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        dri_repository = DRIRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await dri_repository.get_dri_parameters(serial)

        event_bus.rpc_request.assert_awaited_once_with("dri.parameters.request", request, timeout=120)
        notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert result == {"body": err_msg, "status": 400}
