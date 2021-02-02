from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.clients.digi_client import DiGiClient
from asynctest import CoroutineMock
from config import testconfig
from pytest import raises
import humps


class TestDiGiClient:

    def instance_test(self):
        config = testconfig
        logger = Mock()

        digi_client = DiGiClient(config, logger)
        assert digi_client._config == config
        assert digi_client._logger == logger

    @pytest.mark.asyncio
    async def login_test(self):
        config = testconfig
        logger = Mock()

        access_token_str = "Someverysecretaccesstoken"

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={"access_token": access_token_str})

        digi_client = DiGiClient(config, logger)
        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            await digi_client.login()

            assert access_token_str == digi_client._bearer_token
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def login_with_failure_test(self):
        config = testconfig
        logger = Mock()

        digi_client = DiGiClient(config, logger)
        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=Exception)) as mock_post:
            await digi_client.login()

            assert digi_client._bearer_token == ''
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_request_headers_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
                    'velo_serial': 'VC05200046188',
                    'ticket': '3574667',
                    'MAC': '00:04:2d:0b:cf:7f:0000'}

        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {
            "authorization": f"Bearer {access_token_str}",
            'igzID': request_id,
            **payload
        }

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = access_token_str

        headers = digi_client._get_request_headers(request_id, payload)
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def get_request_headers_no_bearer_token_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
                    'velo_serial': 'VC05200046188',
                    'ticket': '3574667',
                    'MAC': '00:04:2d:0b:cf:7f:0000'}

        digi_client = DiGiClient(config, logger)

        with raises(Exception) as error_info:
            headers = digi_client._get_request_headers(request_id, payload)
            assert error_info == "Missing BEARER token"

    @pytest.mark.asyncio
    async def reboot_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
            'velo_serial': 'VC05200046188',
            'ticket': '3574667',
            'MAC': '00:04:2d:0b:cf:7f:0000'}

        get_response = [{"Message": "Success"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {
            "authorization": f"Bearer {digi_client._bearer_token}",
            'igzID': request_id,
            **humps.pascalize(payload)
        }

        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(request_id, payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]['headers'] == expected_headers
            assert digi_reboot == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def reboot_non_2xx_status_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
            'velo_serial': 'VC05200046188',
            'ticket': '3574667',
            'MAC': '00:04:2d:0b:cf:7f:0000'}

        get_response = "ERROR"

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {
            "authorization": f"Bearer {digi_client._bearer_token}",
            'igzID': request_id,
            **humps.pascalize(payload)
        }

        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(request_id, payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]['headers'] == expected_headers
            assert digi_reboot == dict(body=get_response, status=500)

    @pytest.mark.asyncio
    async def reboot_error_field_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
            'velo_serial': 'VC05200046188',
            'ticket': '3574667',
            'MAC': '00:04:2d:0b:cf:7f:0000'}

        get_response = [{"Message": "Failed"}, {'error': "Failed"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {
            "authorization": f"Bearer {digi_client._bearer_token}",
            'igzID': request_id,
            **humps.pascalize(payload)
        }

        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(request_id, payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]['headers'] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_aborted_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        payload = {
            'velo_serial': 'VC05200046188',
            'ticket': '3574667',
            'MAC': '00:04:2d:0b:cf:7f:0000'}

        get_response = [{"Message": "Failed"}, {'Message': "Aborted"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {
            "authorization": f"Bearer {digi_client._bearer_token}",
            'igzID': request_id,
            **humps.pascalize(payload)
        }

        with patch.object(digi_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(request_id, payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]['headers'] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_general_exception_test(self):
        config = testconfig
        logger = Mock()
        request_id = 'test_id'
        get_response = [{"Message": "Failed"}, {'Message': "Aborted"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)

        payload = {
            'velo_serial': 'VC05200046188',
            'ticket': '3574667',
            'MAC': '00:04:2d:0b:cf:7f:0000'}

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"
        error_message = "Failed"
        with patch.object(digi_client._session, 'post', new=CoroutineMock(side_effect=Exception(error_message))) \
                as mock_post:
            digi_reboot = await digi_client.reboot(request_id, payload)

            mock_post.assert_awaited_once()
            assert digi_reboot == dict(body=error_message, status=500)
