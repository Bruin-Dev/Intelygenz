from unittest.mock import AsyncMock, Mock, patch

import pytest
from aiohttp import ClientSession

from application.clients.forticloud_client import ForticloudClient
from config import testconfig as config


@pytest.fixture(scope="function")
def forticloud_client():
    client = ForticloudClient(config=config)
    client._session = Mock(spec_set=ClientSession)
    return client


class TestForticloudClient:
    @pytest.mark.asyncio
    async def instance_test(self, forticloud_client):
        assert forticloud_client._config is config

    @pytest.mark.asyncio
    async def get_request_headers_test(self, forticloud_client):
        forticloud_client._access_token = "token"

        expected_result = {
            "Authorization": f"Bearer token",
        }

        result = forticloud_client._get_request_headers()
        assert result == expected_result


class TestRequest:
    @pytest.mark.asyncio
    async def request_ok_test(self, forticloud_client):
        method = "GET"
        url = "https://forticloud.com/test"
        status = 200
        body = {}

        headers = {
            "Authorization": "Bearer token",
        }

        response = Mock()
        response.status = status
        response.json = AsyncMock(return_value=body)

        request = AsyncMock(return_value=response)

        forticloud_client._get_request_headers = Mock(return_value=headers)

        with patch.object(forticloud_client._session, "request", new=request):
            result = await forticloud_client._request(method=method, url=url)

        expected_result = {"status": status, "body": body}
        forticloud_client._get_request_headers.assert_called_once()
        request.assert_called_once_with(method=method, url=url, headers=headers)
        assert result == expected_result

    @pytest.mark.asyncio
    async def request_unauthorized_test(self, forticloud_client):
        method = "GET"
        url = "https://forticloud.com/test"
        first_status = 401
        second_status = 200
        body = {}

        headers = {
            "Authorization": "Bearer token",
        }

        first_response = Mock()
        first_response.status = first_status
        first_response.json = AsyncMock(return_value=body)

        second_response = Mock()
        second_response.status = second_status
        second_response.json = AsyncMock(return_value=body)

        request = AsyncMock(side_effect=[first_response, second_response])

        forticloud_client._get_request_headers = Mock(return_value=headers)
        forticloud_client._get_access_token = AsyncMock()

        with patch.object(forticloud_client._session, "request", new=request):
            result = await forticloud_client._request(method=method, url=url)

        expected_result = {"status": second_status, "body": body}

        forticloud_client._get_access_token.assert_awaited_once()
        assert forticloud_client._get_request_headers.call_count == 2
        assert request.call_count == 2
        assert result == expected_result

    @pytest.mark.asyncio
    async def request_exception_test(self, forticloud_client):
        method = "GET"
        url = "https://forticloud.com/test"

        headers = {
            "Authorization": "Bearer token",
        }

        request = AsyncMock(return_value=Exception)

        forticloud_client._get_request_headers = Mock(return_value=headers)

        with patch.object(forticloud_client._session, "request", new=request):
            result = await forticloud_client._request(method=method, url=url)

        expected_result = {"status": 500}
        forticloud_client._get_request_headers.assert_called_once()
        request.assert_called_once_with(method=method, url=url, headers=headers)
        assert result == expected_result


class TestGetAccessToken:
    @pytest.mark.asyncio
    async def get_access_token_ok_test(self, forticloud_client):
        access_token = "token"
        status = 200
        body = {"access_token": access_token}

        form_data = {
            "grant_type": "password",
            "client_id": "client_id",
            "username": "username",
            "password": "password",
        }

        response = Mock()
        response.status = status
        response.json = AsyncMock(return_value=body)

        forticloud_client._session.request = AsyncMock(return_value=response)

        assert forticloud_client._access_token == ""
        await forticloud_client._get_access_token()

        assert forticloud_client._access_token == access_token
        forticloud_client._session.request.assert_awaited_once_with(
            method="POST", url="base_url/api/v1/oauth/token", data=form_data
        )

    @pytest.mark.asyncio
    async def get_access_token_unauthorized_test(self, forticloud_client):
        response = Mock()
        response.status = 401

        forticloud_client._session.request = AsyncMock(return_value=response)

        await forticloud_client._get_access_token()

        assert forticloud_client._access_token == ""
        forticloud_client._session.request.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_access_token_exception_test(self, forticloud_client):
        forticloud_client._session.request = AsyncMock(return_value=Exception)

        await forticloud_client._get_access_token()

        assert forticloud_client._access_token == ""
        forticloud_client._session.request.assert_awaited_once()
