from logging import Logger
from typing import Callable, Any
from unittest.mock import Mock, ANY

import aiohttp
import pytest as pytest
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from asynctest import CoroutineMock
from pytest import fixture
from pytest import mark

from application.clients.bruin_session import BruinSession, BruinResponse, COMMON_HEADERS, OK_STATUS


class TestBruinSession:
    @mark.asyncio
    async def get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
        client_response_builder: Callable[..., ClientResponse],
    ):
        url = "any_url"
        path = "any_path"
        access_token = "any_access_token"
        response_status = hash("any_response_status")
        response_body = "any_response_body"
        client_response = client_response_builder(response_body=response_body, status=response_status)
        bruin_session = bruin_session_builder(base_url=url, access_token=access_token)
        bruin_session.session.get = CoroutineMock(return_value=client_response)
        query_params = {"query_param": "value"}

        subject = await bruin_session.get(path=path, query_params=query_params)

        assert subject == BruinResponse(status=response_status, body=response_body)
        bruin_session.session.get.assert_awaited_once_with(
            f"{url}{path}",
            params={"QueryParam": "value"},
            headers={"authorization": f"Bearer {access_token}", **COMMON_HEADERS},
            ssl=False)

    @mark.asyncio
    async def client_connection_error_get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
    ):
        bruin_session = bruin_session_builder()
        bruin_session.session.get = CoroutineMock(side_effect=aiohttp.ClientConnectionError("some error"))

        subject = await bruin_session.get(path=ANY, query_params=ANY)

        assert subject == BruinResponse(status=500, body=f"ClientConnectionError: some error")

    @mark.asyncio
    async def unexpected_error_get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
    ):
        bruin_session = bruin_session_builder()
        bruin_session.session.get = CoroutineMock(side_effect=Exception("some error"))

        subject = await bruin_session.get(path=ANY, query_params=ANY)

        assert subject == BruinResponse(status=500, body=f"Unexpected error: some error")


class TestBruinResponse:
    @mark.asyncio
    async def bruin_responses_are_properly_built_from_client_response_test(
        self,
        client_response_builder
    ):
        response_status = hash("any_status")
        response_body = "any_response_body"
        client_response = client_response_builder(response_body=response_body, status=response_status)

        subject = await BruinResponse.from_client_response(client_response)

        assert subject.status == response_status
        assert subject.body == response_body

    @mark.asyncio
    async def bruin_response_json_errors_fallback_to_text_test(self):
        text = "any_text"
        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(side_effect=ValueError())
        client_response.text = CoroutineMock(return_value=text)

        subject = await BruinResponse.from_client_response(client_response)

        assert subject.body == text

    @mark.asyncio
    async def bruin_responses_raise_proper_error_on_client_response_error_test(self):
        json_error = "json_error"
        text_error = "text_error"
        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(side_effect=ValueError(json_error))
        client_response.text = CoroutineMock(side_effect=ValueError(text_error))

        with pytest.raises(ValueError, match=text_error):
            await BruinResponse.from_client_response(client_response)

    @mark.asyncio
    async def bruin_ok_responses_are_properly_detected_test(self, client_response_builder):
        client_response = client_response_builder(status=OK_STATUS)

        subject = await BruinResponse.from_client_response(client_response)

        assert subject.ok()

    @mark.asyncio
    async def bruin_ko_responses_are_properly_detected_test(self, client_response_builder):
        client_response = client_response_builder(status=400)

        subject = await BruinResponse.from_client_response(client_response)

        assert not subject.ok()


#
# Fixtures
#

@fixture
def bruin_session_builder():
    def builder(
        logger: Logger = Mock(Logger),
        session: ClientSession = Mock(ClientSession),
        base_url: str = "any_url",
        access_token: str = "any_access_token",
    ) -> BruinSession:
        return BruinSession(session=session, base_url=base_url, logger=logger, access_token=access_token)

    return builder


@fixture
def client_response_builder():
    def builder(response_body: Any = None, status: int = 200) -> ClientResponse:
        if response_body is None:
            response_body = "any_response_body"

        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(return_value=response_body)
        client_response.status = status
        return client_response

    return builder
