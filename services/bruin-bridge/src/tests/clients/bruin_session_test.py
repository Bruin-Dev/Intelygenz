from logging import Logger
from typing import Dict, Callable
from unittest.mock import Mock

import aiohttp
import pytest as pytest
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from asynctest import CoroutineMock
from pytest import fixture
from pytest import mark

from application.clients.bruin_session import BruinSession, BruinResponse, COMMON_HEADERS


class TestBruinSession:
    def instance_test(self):
        session, base_url, logger = Mock(), Mock(), Mock()

        subject = BruinSession(session, base_url, logger)

        assert subject.session is session
        assert subject.base_url is base_url
        assert subject.logger is logger

    @mark.asyncio
    async def get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
        client_response_builder: Callable[..., ClientResponse],
        a_response_status: int, a_url: str, a_path: str, an_access_token: str,
        a_response_body: Dict[str, str]
    ):
        bruin_session = bruin_session_builder(base_url=a_url)
        a_client_response = client_response_builder(json=a_response_body, status=a_response_status)
        bruin_session.session.get = CoroutineMock(return_value=a_client_response)
        query_params = {"query_param": "value"}

        subject = await bruin_session.get(path=a_path, access_token=an_access_token, query_params=query_params)

        assert subject == BruinResponse(status=a_response_status, body=a_response_body)
        bruin_session.session.get.assert_awaited_once_with(
            f"{a_url}{a_path}",
            params={"QueryParam": "value"},
            headers={"authorization": f"Bearer {an_access_token}", **COMMON_HEADERS},
            ssl=False)

    @mark.asyncio
    async def client_connection_error_get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
        a_path: str, an_access_token: str, some_query_params: Dict[str, str]
    ):
        bruin_session = bruin_session_builder()
        bruin_session.session.get = CoroutineMock(side_effect=aiohttp.ClientConnectionError("some error"))

        subject = await bruin_session.get(path=a_path, access_token=an_access_token, query_params=some_query_params)

        assert subject == BruinResponse(status=500, body=f"ClientConnectionError: some error")

    @mark.asyncio
    async def unexpected_error_get_requests_are_properly_handled_test(
        self,
        bruin_session_builder: Callable[..., BruinSession],
        a_path: str, an_access_token: str, some_query_params: Dict[str, str]
    ):
        bruin_session = bruin_session_builder()
        bruin_session.session.get = CoroutineMock(side_effect=Exception("some error"))

        subject = await bruin_session.get(path=a_path, access_token=an_access_token, query_params=some_query_params)

        assert subject == BruinResponse(status=500, body=f"Unexpected error: some error")


class TestBruinResponse:
    def instance_test(self):
        status, body = Mock(), Mock()

        subject = BruinResponse(status, body)

        assert subject.status is status
        assert subject.body is body

    @mark.asyncio
    async def bruin_responses_are_properly_built_from_client_response_test(
        self, client_response_builder, a_response_body, a_response_status
    ):
        client_response = client_response_builder(json=a_response_body, status=a_response_status)

        subject = await BruinResponse.from_client_response(client_response)

        assert subject.status is a_response_status
        assert subject.body is a_response_body

    @mark.asyncio
    async def bruin_responses_raise_errors_on_client_response_json_deserializing_error_test(self):
        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(side_effect=ValueError("a value error"))

        with pytest.raises(ValueError, match="a value error"):
            await BruinResponse.from_client_response(client_response)

    @mark.asyncio
    async def bruin_ok_responses_are_properly_detected_test(self, client_response_builder, an_ok_response_status):
        client_response = client_response_builder(status=an_ok_response_status)

        subject = await BruinResponse.from_client_response(client_response)

        assert subject.ok()

    @mark.asyncio
    async def bruin_ko_responses_are_properly_detected_test(self, client_response_builder, a_ko_response_status):
        client_response = client_response_builder(status=a_ko_response_status)

        subject = await BruinResponse.from_client_response(client_response)

        assert not subject.ok()


#
# Fixtures
#

@fixture
def bruin_session_builder(a_url, a_response_body):
    def builder(
        logger: Logger = Mock(Logger), session: ClientSession = Mock(ClientSession), base_url: str = a_url
    ) -> BruinSession:
        return BruinSession(session=session, base_url=base_url, logger=logger)

    return builder


@fixture
def client_response_builder(a_response_body, a_response_status):
    def builder(json: dict = None, status: int = a_response_status) -> ClientResponse:
        if json is None:
            json = a_response_body

        client_response = Mock(ClientResponse)
        client_response.json = CoroutineMock(return_value=json)
        client_response.status = status
        return client_response

    return builder


@fixture
def some_query_params():
    return {"param": "value"}


@fixture
def an_access_token():
    return "access_token"


@fixture
def a_url():
    return "http://localhost"


@fixture
def a_path():
    return "/some/path"


@fixture
def a_response_body():
    return {"key": "value"}


@fixture
def a_response_status():
    return 200


@fixture
def an_ok_response_status():
    return 200


@fixture
def a_ko_response_status():
    return 400
