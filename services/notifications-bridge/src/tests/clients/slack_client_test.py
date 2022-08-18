from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from application.clients.slack_client import SlackResponse
from config import testconfig as config

COMMON_HEADERS = {
    "Content-Type": "application/json",
}


class TestSlackClient:
    @pytest.mark.asyncio
    async def instance_test(self, slack_client):
        assert slack_client.config is config.SLACK_CONFIG
        assert slack_client.url == config.SLACK_CONFIG["webhook"]

    @pytest.mark.asyncio
    async def send_to_slack_test(self, slack_client, client_response):
        test_msg = {"text": "This is a dummy message"}
        response_status = HTTPStatus.OK
        response_body = "any_response_body"
        slack_response = client_response(body=response_body, status=response_status)

        with patch.object(slack_client.session, "post", new=AsyncMock(return_value=slack_response)) as post_mock:
            response = await slack_client.send_to_slack(test_msg)

            post_mock.assert_awaited_once_with(slack_client.url, headers={**COMMON_HEADERS}, json=test_msg, ssl=False)
            assert response == SlackResponse(status=response_status, body=response_body)

    @pytest.mark.asyncio
    async def send_to_slack_with_bad_status_code_test(self, slack_client, client_response):
        test_msg = {"text": "This is a dummy message"}
        response_status = HTTPStatus.BAD_REQUEST
        response_body = "any_response_body"
        slack_response = client_response(body=response_body, status=response_status)

        with patch.object(slack_client.session, "post", new=AsyncMock(return_value=slack_response)) as post_mock:
            response = await slack_client.send_to_slack(test_msg)

            post_mock.assert_called_once_with(slack_client.url, headers={**COMMON_HEADERS}, json=test_msg, ssl=False)
            assert response == SlackResponse(status=response_status, body=response_body)

    @pytest.mark.asyncio
    async def client_connection_error_test(self, slack_client):
        test_msg = {"text": "This is a dummy message"}
        slack_response = AsyncMock(side_effect=aiohttp.ClientConnectionError("client error"))

        with patch.object(slack_client.session, "post", new=slack_response):
            response = await slack_client.send_to_slack(test_msg)

            assert response == SlackResponse(
                status=HTTPStatus.INTERNAL_SERVER_ERROR, body="ClientConnectionError: client error"
            )

    @pytest.mark.asyncio
    async def client_exception_test(self, slack_client):
        test_msg = {"text": "This is a dummy message"}

        with pytest.raises(Exception) as random_exception:
            await slack_client.send_to_slack(test_msg)

            assert random_exception == SlackResponse(
                status=HTTPStatus.INTERNAL_SERVER_ERROR, body="ClientConnectionError: client error"
            )
