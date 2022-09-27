from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import ANY
from unittest.mock import AsyncMock as _AsyncMock
from unittest.mock import Mock

import pytest
from aiohttp import ClientResponse

from client import TOKEN_FORM_DATA, TOKEN_METHOD, TOKEN_PATH, BruinClient
from models import BruinCredentials, BruinRequest, BruinResponse, BruinToken, RefreshTokenError


async def requests_are_properly_sent_test(any_bruin_client, any_request, any_response):
    # given
    http_request = AsyncMock(return_value=any_response())
    bruin_client = any_bruin_client(http_request=http_request)

    # when
    await bruin_client.send(any_request)

    # then
    http_request.assert_awaited_once_with_partial(
        method=any_request.method,
        url=any_request.path,
        json=any_request.json,
        params=any_request.query_params,
    )


async def request_headers_are_properly_sent_test(any_bruin_client, any_request, any_response, any_valid_token):
    # given
    any_valid_token.value = "any_access_token"
    any_request.headers = {"any-header": "any-value"}
    http_request = AsyncMock(return_value=any_response())
    bruin_client = any_bruin_client(http_request=http_request, bruin_token=any_valid_token)

    # when
    await bruin_client.send(any_request)

    # then
    http_request.assert_awaited_once_with_partial(
        headers={
            "any-header": "any-value",
            "authorization": f"Bearer any_access_token",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
    )


async def request_headers_are_properly_overwritten_test(any_bruin_client, any_request, any_response, any_valid_token):
    # given
    any_valid_token.value = "any_access_token"
    any_request.headers = {"Content-Type": "any-content-type"}
    http_request = AsyncMock(return_value=any_response())
    bruin_client = any_bruin_client(http_request=http_request, bruin_token=any_valid_token)

    # when
    await bruin_client.send(any_request)

    # then
    http_request.assert_awaited_once_with_partial(
        headers={
            "authorization": f"Bearer any_access_token",
            "Content-Type": "any-content-type",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
    )


async def responses_are_properly_built_test(any_bruin_client, any_request, any_response, any_valid_token):
    # given
    http_request = AsyncMock(return_value=any_response(status=1, text="any_text"))
    bruin_client = any_bruin_client(http_request=http_request)

    # then
    assert await bruin_client.send(any_request) == BruinResponse(status=1, text="any_text")


async def expired_tokens_are_automatically_refreshed_test(any_bruin_client, any_request, any_expired_token):
    # given
    refresh_token = AsyncMock()
    bruin_client = any_bruin_client(refresh_token=refresh_token, bruin_token=any_expired_token)

    # when
    await bruin_client.send(any_request)

    # then
    refresh_token.assert_awaited_once()


async def valid_tokens_are_never_refreshed_test(any_bruin_client, any_request, any_valid_token):
    # given
    refresh_token = AsyncMock()
    bruin_client = any_bruin_client(refresh_token=refresh_token, bruin_token=any_valid_token)

    # when
    await bruin_client.send(any_request)

    # then
    refresh_token.assert_not_awaited()


async def tokens_are_properly_refreshed_test(any_bruin_client, any_response):
    # given
    http_request = AsyncMock(return_value=any_response(text='{"access_token":"any_access_token","expires_in":1}'))
    bruin_client = any_bruin_client(http_request=http_request)

    # when
    await bruin_client.refresh_token()

    # then
    assert bruin_client.token == BruinToken(value="any_access_token", expires_in=1, issued_at=ANY)


async def token_refresh_error_status_raise_a_proper_exception_test(any_bruin_client, any_response):
    # given
    bruin_client = any_bruin_client(http_request=AsyncMock(return_value=any_response(status=400)))

    # then
    with pytest.raises(RefreshTokenError):
        await bruin_client.refresh_token()


async def non_parseable_token_responses_raise_a_proper_exception_test(any_bruin_client, any_response):
    # given
    bruin_client = any_bruin_client(http_request=AsyncMock(return_value=any_response(text="non_parseable_data")))

    # then
    with pytest.raises(RefreshTokenError):
        await bruin_client.refresh_token()


@pytest.fixture
def any_bruin_client(any_response, any_credentials, any_valid_token):
    def builder(
        http_request: AsyncMock = AsyncMock(return_value=any_response()),
        bruin_credentials: BruinCredentials = any_credentials(),
        bruin_token: BruinToken = any_valid_token,
        refresh_token: Optional[AsyncMock] = None,
    ):
        bruin_client = BruinClient(base_url="http://localhost", credentials=bruin_credentials)
        bruin_client.token = bruin_token
        bruin_client.session.request = http_request
        if refresh_token:
            bruin_client.refresh_token = refresh_token

        return bruin_client

    return builder


@pytest.fixture
def any_request():
    return BruinRequest(
        path="/",
        method="GET",
        query_params={"any_param": "any_value"},
        headers={"any_header": "any_value"},
        json='"any_json"',
    )


@pytest.fixture
def any_response():
    def builder(
        status: int = 200,
        text: str = "",
    ):
        client_response = Mock(ClientResponse)
        client_response.status = status
        client_response.text = AsyncMock(return_value=text)

        return client_response

    return builder


@pytest.fixture
def any_valid_token():
    return BruinToken(issued_at=datetime.utcnow() + timedelta(minutes=1))


@pytest.fixture
def any_expired_token():
    return BruinToken(issued_at=datetime.utcnow() - timedelta(minutes=1))


@pytest.fixture
def refresh_args_for():
    def builder(bruin_credentials: BruinCredentials):
        return dict(
            method=TOKEN_METHOD,
            url=TOKEN_PATH,
            data=TOKEN_FORM_DATA,
            headers={
                "authorization": f"Basic {bruin_credentials.b64encoded()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    return builder


@pytest.fixture
def any_credentials():
    def builder(b64encoded: str = "any_base64_credentials"):
        bruin_credentials = BruinCredentials(client_id="any_client_id", client_secret="any_client_secret")
        bruin_credentials.b64encoded = Mock(return_value=b64encoded)
        return bruin_credentials

    return builder


class AsyncMock(_AsyncMock):
    def assert_awaited_once_with_partial(self, *args, **kwargs):
        self.assert_awaited_once()
        args_match = all(arg in self.call_args.args for arg in args)
        kwargs_match = kwargs.items() <= self.call_args.kwargs.items()
        if not args_match or not kwargs_match:
            raise AssertionError(self._format_mock_failure_message(args, kwargs, action="await"))
