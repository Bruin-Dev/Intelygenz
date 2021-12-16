import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import humps
import pytest

from aiohttp import ClientConnectionError

from asynctest import CoroutineMock
from pytest import raises

from application.clients.dri_client import DRIClient
from config import testconfig as config


class TestDRIClient:

    def instance_test(self):
        logger = Mock()

        dri_client = DRIClient(config, logger)

        assert dri_client._logger is logger
        assert dri_client._config is config

    @pytest.mark.asyncio
    async def login_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={"authorization_token": access_token_str})

        dri_client = DRIClient(config, logger)
        with patch.object(dri_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            await dri_client.login()

            assert dri_client._bearer_token == access_token_str
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def login_with_failure_test(self):
        logger = Mock()

        dri_client = DRIClient(config, logger)
        with patch.object(dri_client._session, 'post', new=CoroutineMock(return_value=Exception)) as mock_post:
            await dri_client.login()

            assert dri_client._bearer_token == ''
            mock_post.assert_called_once()

    def get_request_headers_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {
            "authorization": f"Bearer {access_token_str}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = access_token_str

        headers = dri_client._get_request_headers()
        assert headers == expected_headers

    def get_request_headers_with_no_bearer_token_test(self):
        logger = Mock()
        dri_client = DRIClient(config, logger)

        with raises(Exception) as error_info:
            dri_client._get_request_headers()
            assert error_info == "Missing BEARER token"

    @pytest.mark.asyncio
    async def get_task_id_200_success_test(self):
        serial = '700059'
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
        get_response = {'status': 'SUCCESS',
                        'message': 'All Good!',
                        'data': {
                            'Id': 1725608,
                            'ErrorCode': 100,
                            'Message': ''}
                        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_id = await dri_client.get_task_id(serial, parameter_set)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_id['body'] == get_response
            assert task_id['status'] == 200

    @pytest.mark.asyncio
    async def get_task_id_non_2xx_failed_test(self):
        serial = '700059'

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

        get_response = {'status': 'FAILED',
                        'message': 'FAILED',
                        'data': {}
                        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_id = await dri_client.get_task_id(serial, parameter_set)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_id['body'] == get_response
            assert task_id['status'] == 400

    @pytest.mark.asyncio
    async def get_task_id_401_login_failed_test(self):
        serial = '700059'

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

        response_mock = CoroutineMock()
        response_mock.status = 401

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_id = await dri_client.get_task_id(serial, parameter_set)
            mock_get.assert_called_once()
            dri_client.login.assert_awaited_once()
            assert task_id['body'] == "Got 401 from DRI"
            assert task_id['status'] == 401

    @pytest.mark.asyncio
    async def get_task_id_504_login_failed_test(self):
        serial = '700059'

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

        response_mock = CoroutineMock()
        response_mock.status = 504

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_id = await dri_client.get_task_id(serial, parameter_set)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_id['body'] == f"Getting task_id of {serial} timed out"
            assert task_id['status'] == 504

    @pytest.mark.asyncio
    async def get_task_id_exception_failed_test(self):
        serial = '700059'

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

        err_msg = "Failed"

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(side_effect=Exception(err_msg))) as mock_get:
            task_id = await dri_client.get_task_id(serial, parameter_set)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_id['body'] == err_msg
            assert task_id['status'] == 500

    @pytest.mark.asyncio
    async def get_task_results_200_success_test(self):
        serial = '700059'
        task_id = 1725608

        get_response = {'status': 'SUCCESS', 'message': 'All Good!', 'data': {
                'Parameters': [
                    {'Name': 'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei',
                     'Value': '864839040023968',
                     'ErrorCode': 100, 'Message': ''}], 'ErrorCode': 100, 'Message': ''}}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_results = await dri_client.get_task_results(serial, task_id)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_results['body'] == get_response
            assert task_results['status'] == 200

    @pytest.mark.asyncio
    async def get_task_results_non_2xx_failed_test(self):
        serial = '700059'
        task_id = 1725608

        get_response = {'status': 'FAILED', 'message': 'Failed'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_results = await dri_client.get_task_results(serial, task_id)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_results['body'] == get_response
            assert task_results['status'] == 400

    @pytest.mark.asyncio
    async def get_task_results_401_login_failed_test(self):
        serial = '700059'
        task_id = 1725608

        response_mock = CoroutineMock()
        response_mock.status = 401

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            task_results = await dri_client.get_task_results(serial, task_id)
            mock_get.assert_called_once()
            dri_client.login.assert_awaited_once()
            assert task_results['body'] == "Got 401 from DRI"
            assert task_results['status'] == 401

    @pytest.mark.asyncio
    async def get_task_results_exception_failed_test(self):
        serial = '700059'
        task_id = 1725608

        err_msg = "Failed"

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(side_effect=Exception(err_msg))) as mock_get:
            task_results = await dri_client.get_task_results(serial, task_id)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert task_results['body'] == err_msg
            assert task_results['status'] == 500

    @pytest.mark.asyncio
    async def get_pending_task_ids_200_success_test(self):
        serial = '700059'
        get_response = {'status': 'SUCCESS', 'message': 'All Good!', 'data': {'Transactions': [{"Ids": 17000}],
                                                                              'ErrorCode': 100,
                                                                              'Message': ''}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            pending_task_ids = await dri_client.get_pending_task_ids(serial)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert pending_task_ids['body'] == get_response
            assert pending_task_ids['status'] == 200

    @pytest.mark.asyncio
    async def get_pending_task_ids_non_2xx_test(self):
        serial = '700059'
        get_response = {'status': 'Failed', 'message': 'Failed'}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            pending_task_ids = await dri_client.get_pending_task_ids(serial)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert pending_task_ids['body'] == get_response
            assert pending_task_ids['status'] == 400

    @pytest.mark.asyncio
    async def get_pending_task_ids_401_login_failed_test(self):
        serial = '700059'
        response_mock = CoroutineMock()
        response_mock.status = 401

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            pending_task_ids = await dri_client.get_pending_task_ids(serial)
            mock_get.assert_called_once()
            dri_client.login.assert_awaited_once()
            assert pending_task_ids['body'] == "Got 401 from DRI"
            assert pending_task_ids['status'] == 401

    @pytest.mark.asyncio
    async def get_pending_task_ids_exception_failed_test(self):
        serial = '700059'

        err_msg = "Failed"

        logger = Mock()

        dri_client = DRIClient(config, logger)
        dri_client._bearer_token = "Someverysecretaccesstoken"
        dri_client.login = CoroutineMock()

        with patch.object(dri_client._session, 'get', new=CoroutineMock(side_effect=Exception(err_msg))) as mock_get:
            pending_task_ids = await dri_client.get_pending_task_ids(serial)
            mock_get.assert_called_once()
            dri_client.login.assert_not_awaited()
            assert pending_task_ids['body'] == err_msg
            assert pending_task_ids['status'] == 500
