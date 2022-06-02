from unittest.mock import Mock, patch

import humps
import pytest
from application.clients.digi_client import DiGiClient
from asynctest import CoroutineMock
from config import testconfig
from pytest import raises


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
        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            await digi_client.login()

            assert access_token_str == digi_client._bearer_token
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def login_with_failure_test(self):
        config = testconfig
        logger = Mock()

        digi_client = DiGiClient(config, logger)
        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=Exception)) as mock_post:
            await digi_client.login()

            assert digi_client._bearer_token == ""
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_request_headers_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {"authorization": f"Bearer {access_token_str}", **payload}

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = access_token_str

        headers = digi_client._get_request_headers(payload)
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def get_request_headers_no_bearer_token_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        digi_client = DiGiClient(config, logger)

        with raises(Exception) as error_info:
            headers = digi_client._get_request_headers(payload)
            assert error_info == "Missing BEARER token"

    @pytest.mark.asyncio
    async def reboot_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Success"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def reboot_non_2xx_status_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = "ERROR"

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=500)

    @pytest.mark.asyncio
    async def reboot_error_field_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Failed"}, {"error": "Failed"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_aborted_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Failed"}, {"Message": "Aborted"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(payload)

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_general_exception_test(self):
        config = testconfig
        logger = Mock()
        request_id = "test_id"
        get_response = [{"Message": "Failed"}, {"Message": "Aborted"}]

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)

        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"
        error_message = "Failed"
        with patch.object(
            digi_client._session, "post", new=CoroutineMock(side_effect=Exception(error_message))
        ) as mock_post:
            digi_reboot = await digi_client.reboot(payload)

            mock_post.assert_awaited_once()
            assert digi_reboot == dict(body=error_message, status=500)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        config = testconfig
        logger = Mock()

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
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
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(payload)

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        config = testconfig
        logger = Mock()

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
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
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(payload)

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_error_test(self):
        config = testconfig
        logger = Mock()

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
            "Error": {"Code": "40002", "Message": '"The StartTime ("+StartDateTime+") was not a valid timestamp..."'}
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(payload)

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_non_2xx_test(self):
        config = testconfig
        logger = Mock()

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {"Failure": {}}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 400

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(payload)

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=500)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_general_exception_test(self):
        config = testconfig
        logger = Mock()

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
            "Error": {"Code": "40002", "Message": '"The StartTime ("+StartDateTime+") was not a valid timestamp..."'}
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        digi_client = DiGiClient(config, logger)
        digi_client._bearer_token = "Someverysecretaccesstoken"

        expected_headers = {"authorization": f"Bearer {digi_client._bearer_token}", **humps.pascalize(payload)}
        error_message = "Failed"

        with patch.object(
            digi_client._session, "get", new=CoroutineMock(side_effect=Exception(error_message))
        ) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(payload)

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=error_message, status=500)
