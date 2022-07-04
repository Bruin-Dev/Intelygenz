from unittest.mock import Mock, patch

import pytest
from application.clients.servicenow_client import ServiceNowClient
from asynctest import CoroutineMock
from config import testconfig as config


class TestServiceNowClient:
    def instance_test(self):
        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)

        assert servicenow_client._logger is logger
        assert servicenow_client._config is config

    def get_request_headers_test(self):
        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._access_token = "token"

        expected_result = {
            "Authorization": f"Bearer token",
        }

        result = servicenow_client._get_request_headers()
        assert result == expected_result


class TestRequest:
    @pytest.mark.asyncio
    async def request_ok_test(self):
        method = "GET"
        url = "https://servicenow.com/test"
        status = 200
        body = {}

        headers = {
            "Authorization": "Bearer token",
        }

        response = Mock()
        response.status = status
        response.json = CoroutineMock(return_value=body)

        request = CoroutineMock(return_value=response)

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._get_request_headers = Mock(return_value=headers)

        with patch.object(servicenow_client._client, "request", new=request):
            result = await servicenow_client._request(method=method, url=url)

        expected_result = {"status": status, "body": body}
        servicenow_client._get_request_headers.assert_called_once()
        request.assert_called_once_with(method=method, url=url, headers=headers)
        assert result == expected_result

    @pytest.mark.asyncio
    async def request_unauthorized_test(self):
        method = "GET"
        url = "https://servicenow.com/test"
        first_status = 401
        second_status = 200
        body = {}

        headers = {
            "Authorization": "Bearer token",
        }

        first_response = Mock()
        first_response.status = first_status
        first_response.json = CoroutineMock(return_value=body)

        second_response = Mock()
        second_response.status = second_status
        second_response.json = CoroutineMock(return_value=body)

        request = CoroutineMock(side_effect=[first_response, second_response])

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._get_request_headers = Mock(return_value=headers)
        servicenow_client._get_access_token = CoroutineMock()

        with patch.object(servicenow_client._client, "request", new=request):
            result = await servicenow_client._request(method=method, url=url)

        expected_result = {"status": second_status, "body": body}

        servicenow_client._get_access_token.assert_awaited_once()
        assert servicenow_client._get_request_headers.call_count == 2
        assert request.call_count == 2
        assert result == expected_result

    @pytest.mark.asyncio
    async def request_exception_test(self):
        method = "GET"
        url = "https://servicenow.com/test"

        headers = {
            "Authorization": "Bearer token",
        }

        request = CoroutineMock(return_value=Exception)

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._get_request_headers = Mock(return_value=headers)

        with patch.object(servicenow_client._client, "request", new=request):
            result = await servicenow_client._request(method=method, url=url)

        expected_result = {"status": 500}
        servicenow_client._get_request_headers.assert_called_once()
        request.assert_called_once_with(method=method, url=url, headers=headers)
        servicenow_client._logger.exception.assert_called_once()
        assert result == expected_result


class TestGetAccessToken:
    @pytest.mark.asyncio
    async def get_access_token_ok_test(self):
        access_token = "token"
        status = 200
        body = {"access_token": access_token}

        form_data = {
            "grant_type": "password",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "username": "username",
            "password": "password",
        }

        response = Mock()
        response.status = status
        response.json = CoroutineMock(return_value=body)

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._client = Mock()
        servicenow_client._client.request = CoroutineMock(return_value=response)

        assert servicenow_client._access_token == ""
        await servicenow_client._get_access_token()

        assert servicenow_client._access_token == access_token
        servicenow_client._client.request.assert_awaited_once_with(
            method="POST", url="base_url/oauth_token.do", data=form_data
        )

    @pytest.mark.asyncio
    async def get_access_token_unauthorized_test(self):
        response = Mock()
        response.status = 401

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._client = Mock()
        servicenow_client._client.request = CoroutineMock(return_value=response)

        await servicenow_client._get_access_token()

        assert servicenow_client._access_token == ""
        servicenow_client._client.request.assert_awaited_once()
        servicenow_client._logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def get_access_token_exception_test(self):
        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._client = Mock()
        servicenow_client._client.request = CoroutineMock(return_value=Exception)

        await servicenow_client._get_access_token()

        assert servicenow_client._access_token == ""
        servicenow_client._client.request.assert_awaited_once()
        servicenow_client._logger.exception.assert_called_once()


class TestReportIncident:
    @pytest.mark.asyncio
    async def report_incident_test(self):
        status = 200
        response_body = {}
        request_body = {}

        response = Mock()
        response.status = status
        response.json = CoroutineMock(return_value=response_body)

        logger = Mock()
        servicenow_client = ServiceNowClient(logger, config)
        servicenow_client._request = CoroutineMock(return_value=response)

        result = await servicenow_client.report_incident(request_body)

        servicenow_client._request.assert_awaited_once_with(
            method="POST", url="base_url/api/g_mtcm/intelygenz", json=request_body
        )
        assert result == response
