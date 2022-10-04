from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import humps
import pytest
from aiohttp import ClientSession
from pytest import raises

from application.clients.digi_client import DiGiClient
from config import testconfig


@pytest.fixture(scope="function")
async def digi_client():
    client = DiGiClient(config=testconfig)
    await client.create_session()
    return client


class TestDiGiClient:
    @pytest.mark.asyncio
    async def login_test(self, digi_client):

        access_token_str = "Someverysecretaccesstoken"

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value={"access_token": access_token_str, "expires_in": 3600})

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            await digi_client.login()

            assert access_token_str == digi_client.bearer_token
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def login_with_failure_test(self, digi_client):

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=Exception)) as mock_post:
            await digi_client.login()

            assert digi_client.bearer_token == ""
            mock_post.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_request_headers_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {"authorization": f"Bearer {access_token_str}", **payload}

        digi_client.bearer_token = access_token_str

        headers = digi_client.get_request_headers(payload)
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def get_request_headers_no_bearer_token_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        with raises(Exception) as error_info:
            headers = digi_client._get_request_headers(payload)
            assert error_info == "Missing BEARER token"

    @pytest.mark.asyncio
    async def reboot_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Success"}]

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(humps.pascalize(payload))

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def reboot_not_set_token_test(self, digi_client):
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": "test_id",
        }

        digi_client.bearer_token = ""

        digi_reboot_response = await digi_client.reboot(humps.pascalize(payload))

        assert (
            digi_reboot_response["status"] == 401
            and digi_reboot_response["body"] == "The token is not created yet. Please try in a few seconds"
        )

    @pytest.mark.asyncio
    async def reboot_non_2xx_status_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Failed", "error": "ERROR"}]

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 400

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(humps.pascalize(payload))

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=500)

    @pytest.mark.asyncio
    async def reboot_error_field_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Failed"}, {"error": "Failed"}]

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(humps.pascalize(payload))

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_aborted_test(self, digi_client):
        request_id = "test_id"
        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        get_response = [{"Message": "Failed"}, {"Message": "Aborted"}]

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "post", new=AsyncMock(return_value=response_mock)) as mock_post:
            digi_reboot = await digi_client.reboot(humps.pascalize(payload))

            mock_post.assert_awaited_once()
            assert mock_post.call_args[1]["headers"] == expected_headers
            assert digi_reboot == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def reboot_general_exception_test(self, digi_client):
        request_id = "test_id"
        get_response = [{"Message": "Failed"}, {"Message": "Aborted"}]

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)

        payload = {
            "velo_serial": "VC05200046188",
            "ticket": "3574667",
            "MAC": "00:04:2d:0b:cf:7f:0000",
            "igzID": request_id,
        }

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)
        error_message = "Failed"
        with patch.object(
            digi_client.session, "post", new=AsyncMock(side_effect=Exception(error_message))
        ) as mock_post:
            digi_reboot = await digi_client.reboot(humps.pascalize(payload))

            mock_post.assert_awaited_once()
            assert digi_reboot == dict(body=error_message, status=500)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self, digi_client):

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

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "get", new=AsyncMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(humps.pascalize(payload))

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=200)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_not_token_set_test(self, digi_client):
        payload = {"igzID": "request_id", "start_date_time": "2021-02-15T16:08:26Z"}

        digi_client.bearer_token = ""

        digi_recovery_logs_response = await digi_client.get_digi_recovery_logs(humps.pascalize(payload))

        assert (
            digi_recovery_logs_response["status"] == 401
            and digi_recovery_logs_response["body"] == "The token is not created yet. Please try in a few seconds"
        )

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_error_test(self, digi_client):

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
            "Error": {"Code": "40002", "Message": '"The StartTime ("+StartDateTime+") was not a valid timestamp..."'}
        }

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "get", new=AsyncMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(humps.pascalize(payload))

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=400)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_non_2xx_test(self, digi_client):

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {"Failure": {}}

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 400

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}

        with patch.object(digi_client.session, "get", new=AsyncMock(return_value=response_mock)) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(humps.pascalize(payload))

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=get_response, status=500)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_general_exception_test(self, digi_client):

        request_id = "test_id"
        payload = {"igzID": request_id, "start_date_time": "2021-02-15T16:08:26Z"}

        get_response = {
            "Error": {"Code": "40002", "Message": '"The StartTime ("+StartDateTime+") was not a valid timestamp..."'}
        }

        response_mock = AsyncMock()
        response_mock.json = AsyncMock(return_value=get_response)
        response_mock.status = 200

        digi_client.bearer_token = "Someverysecretaccesstoken"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)

        expected_headers = {"authorization": f"Bearer {digi_client.bearer_token}", **humps.pascalize(payload)}
        error_message = "Failed"

        with patch.object(digi_client.session, "get", new=AsyncMock(side_effect=Exception(error_message))) as mock_get:
            digi_recovery_logs = await digi_client.get_digi_recovery_logs(humps.pascalize(payload))

            mock_get.assert_awaited_once()
            assert mock_get.call_args[1]["headers"] == expected_headers
            assert digi_recovery_logs == dict(body=error_message, status=500)

    @staticmethod
    async def get_create_session_digi_client_return_not_none_test():
        digi_client = DiGiClient(config=testconfig)
        await digi_client.create_session()
        assert digi_client.session is not None

    @staticmethod
    async def get_create_session_digi_client_return_a_client_session_test():
        digi_client = DiGiClient(config=testconfig)
        await digi_client.create_session()
        assert type(digi_client.session) is ClientSession

    @staticmethod
    def check_if_token_is_created_and_valid_return_not_none_test():
        digi_client = DiGiClient(config=testconfig)
        is_valid_token, error_token_msg = digi_client.check_if_token_is_created_and_valid()
        assert is_valid_token is not None and error_token_msg is not None

    @staticmethod
    def check_if_token_is_created_and_valid_return_a_boolean_and_string_test():
        digi_client = DiGiClient(config=testconfig)
        is_valid_token, error_token_msg = digi_client.check_if_token_is_created_and_valid()
        assert type(is_valid_token) is bool and type(error_token_msg) is str

    @staticmethod
    def check_if_token_is_created_and_valid_return_not_created_token_test():
        digi_client = DiGiClient(config=testconfig)
        digi_client.bearer_token = ""
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)
        is_valid_token, error_token_msg = digi_client.check_if_token_is_created_and_valid()
        assert is_valid_token is False and error_token_msg == f"The token is not created yet"

    @staticmethod
    def check_if_token_is_created_and_valid_return_expires_date_token_test():
        digi_client = DiGiClient(config=testconfig)
        digi_client.bearer_token = "example_token"
        digi_client.expiration_date_for_token = datetime.utcnow() - timedelta(seconds=3600)
        is_valid_token, error_token_msg = digi_client.check_if_token_is_created_and_valid()
        assert is_valid_token is False and error_token_msg == f"The token is not valid because it is expired"

    @staticmethod
    def check_if_token_is_created_and_valid_return_correct_and_none_message_test():
        digi_client = DiGiClient(config=testconfig)
        digi_client.bearer_token = "example_token"
        digi_client.expiration_date_for_token = datetime.utcnow() + timedelta(seconds=3600)
        is_valid_token, error_token_msg = digi_client.check_if_token_is_created_and_valid()
        assert is_valid_token is True and error_token_msg is None
