from typing import Any
from unittest.mock import AsyncMock, Mock, call

import pytest
from aiohttp import ClientResponse, ClientSession
from pydantic import BaseModel

from http_client import BeforeRequestHook, HttpClient, HttpRequest


class AnyBaseModel(BaseModel):
    a_string: str
    an_int: int


@pytest.mark.parametrize(
    ("data", "expected_data"),
    [
        (None, None),
        (1, "1"),
        (True, "true"),
        ("any_string", '"any_string"'),
        (["string_1", "string_2"], '["string_1","string_2"]'),
        ({"a_string": "any_string", "an_int": 1}, '{"a_string":"any_string","an_int":1}'),
        ([{"a_string": "any_string"}, {"an_int": 1}], '[{"a_string":"any_string"},{"an_int":1}]'),
        (AnyBaseModel(a_string="any_string", an_int=1), '{"a_string":"any_string","an_int":1}'),
    ],
    ids=[
        "no data",
        "int data",
        "bool data",
        "string data",
        "list data",
        "dict data",
        "dict list data",
        "base model data",
    ],
)
async def request_data_is_properly_being_serialized_test(
    scenario,
    any_request,
    any_response,
    data,
    expected_data,
):
    # given
    any_request.data = data
    request = AsyncArgsMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request)

    # then
    request.assert_awaited_once_with_args(json=expected_data)


async def non_json_serializable_request_data_raise_an_error_test(scenario, any_request, any_response):
    # given
    any_request.data = {1, 2, 3}
    request = AsyncMock(return_value=any_response)
    http_client = scenario(request)

    # then
    with pytest.raises(TypeError):
        await http_client.send(any_request)


@pytest.mark.parametrize(
    ("path", "path_params", "expected_path"),
    [
        ("/any_path/any_subpath", {}, "/any_path/any_subpath"),
        ("/any_path/${any_param}", {"any_param": "any_value"}, "/any_path/any_value"),
        ("/${param_1}/${param_2}", {"param_1": "value_1", "param_2": "value_2"}, "/value_1/value_2"),
    ],
    ids=[
        "no params path",
        "single param path",
        "multiple params path",
    ],
)
async def request_paths_are_properly_built_test(
    scenario,
    any_request,
    any_response,
    path,
    path_params,
    expected_path,
):
    # given
    any_request.path = path
    any_request.path_params = path_params
    request = AsyncArgsMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request)

    # then
    request.assert_awaited_once_with_args(url=expected_path)


async def requests_are_made_using_the_correct_method_test(scenario, any_request, any_response):
    # given
    any_request.method = "any_method"
    request = AsyncArgsMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request)

    # then
    request.assert_awaited_once_with_args(method="any_method")


async def requests_headers_are_properly_being_set_test(scenario, any_request, any_response):
    # given
    any_request.headers = {"any_header": "any_value"}
    request = AsyncArgsMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request)

    # then
    request.assert_awaited_once_with_args(headers={"any_header": "any_value"})


@pytest.mark.parametrize(
    ("response_data", "expected_data", "response_type"),
    [
        ("", None, None),
        ("", None, int),
        ("", None, str),
        ("", None, bool),
        ("1", 1, None),
        ("1", 1, int),
        ("1", "1", str),
        ("true", True, None),
        ("1", True, bool),
        ("0", True, bool),
        ('"any_string"', "any_string", None),
        ('"any_string"', '"any_string"', str),
        ('["string_1", "string_2"]', ["string_1", "string_2"], None),
        ('{"a_string":"any_string","an_int":1}', {"a_string": "any_string", "an_int": 1}, None),
        ('[{"a_string":"any_string"},{"an_int":1}]', [{"a_string": "any_string"}, {"an_int": 1}], None),
        ('[{"a_string":"any_string"},{"an_int":1}]', [{"a_string": "any_string"}, {"an_int": 1}], Any),
        ('{"a_string":"any_string","an_int":1}', AnyBaseModel(a_string="any_string", an_int=1), AnyBaseModel),
        ('{"a_string":"any_string","an_int":"1"}', AnyBaseModel(a_string="any_string", an_int=1), AnyBaseModel),
    ],
    ids=[
        "empty response to default(json)",
        "empty response to int",
        "empty response to str",
        "empty response to bool",
        "int response to default(json)",
        "int response to int",
        "int response to str",
        "boolean string response to default(json)",
        "boolean true string response to bool",
        "boolean false string response to bool",
        "json string response to default(json)",
        "json string response to str",
        "json list response to default(json)",
        "json dict response to default(json)",
        "json dict list response to default(json)",
        "json dict list response to Any",
        "json dict response to pydantic model",
        "json dict response with different types to pydantic model",
    ],
)
async def responses_are_properly_deserialized_test(
    scenario,
    any_request,
    a_response,
    response_data,
    expected_data,
    response_type,
):
    # given
    request = AsyncMock(return_value=a_response(response_data))
    http_client = scenario(request)

    # when
    http_response = await http_client.send(any_request, response_type=response_type)

    # then
    assert http_response.data == expected_data


@pytest.mark.parametrize(
    ("response_data", "response_type"),
    [
        ("any_string", None),
        ("any_string", int),
        ("any_string", AnyBaseModel),
        ("[]", AnyBaseModel),
        ('{"a_string":"any_string"}', AnyBaseModel),
        ('{"a_string":"any_string","an_int":"any_string"}', AnyBaseModel),
    ],
    ids=[
        "string response to default(json)",
        "string response to int",
        "string response to pydantic model",
        "json list response to pydantic model",
        "json dict with missing fields to pydantic model",
        "json dict with wrong type fields to pydantic model",
    ],
)
async def deserialization_errors_are_properly_propagated_test(
    scenario,
    any_request,
    a_response,
    response_data,
    response_type,
):
    # given
    request = AsyncMock(return_value=a_response(response_data))
    http_client = scenario(request)

    # then
    with pytest.raises(ValueError):
        await http_client.send(any_request, response_type=response_type)


async def keyword_args_are_properly_sent_test(scenario, any_request, any_response):
    # given
    request = AsyncArgsMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request, any_keyword_arg="any_value")

    # then
    request.assert_awaited_once_with_args(any_keyword_arg="any_value")


async def before_request_hooks_are_executed_before_requests_test(scenario, any_request, any_response):
    # given
    mock = Mock()
    mock.before_request_hook = AsyncMock()
    mock.request = AsyncMock(return_value=any_response)
    http_client = scenario(mock.request)

    # when
    await http_client.send(any_request, before_request_hook=mock.before_request_hook)

    # then
    expected_calls = [
        call.before_request_hook(http_client=http_client, http_request=any_request, response_type=None),
        call.request(method=any_request.method, url=any_request.path, json=None, headers=any_request.headers),
    ]
    mock.assert_has_calls(expected_calls)


async def before_request_hooks_are_properly_executed_test(scenario, any_request, any_response):
    # given
    before_request_hook = AsyncMock()
    request = AsyncMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(
        any_request, response_type=Any, before_request_hook=before_request_hook, any_keyword_arg="value"
    )

    # then
    before_request_hook.assert_awaited_once_with(
        http_client=http_client,
        http_request=any_request,
        response_type=Any,
        any_keyword_arg="value",
    )


async def before_request_hooks_can_update_the_request_test(scenario, any_request, any_response):
    # given
    class AnyBeforeRequestHook(BeforeRequestHook):
        async def __call__(self, http_request: HttpRequest, **kwargs):
            http_request.headers["any_header"] = "any_value"

    any_request.headers = {}
    before_request_hook = AnyBeforeRequestHook()
    request = AsyncMock(return_value=any_response)
    http_client = scenario(request)

    # when
    await http_client.send(any_request, before_request_hook=before_request_hook)

    # then
    assert any_request.headers == {"any_header": "any_value"}


async def http_client_is_properly_closed_test(scenario):
    # given
    close = AsyncMock()
    http_client = scenario(close=close)

    # when
    await http_client.close()

    # then
    close.assert_awaited_once()


@pytest.fixture
def scenario(any_response):
    def builder(request: AsyncMock = AsyncMock(return_value=any_response), close: AsyncMock = AsyncMock()):
        client_session = Mock(ClientSession)
        client_session.request = request
        client_session.close = close

        return HttpClient(client_session)

    return builder


@pytest.fixture
def any_request():
    return HttpRequest(path="/", method="GET")


@pytest.fixture
def any_response(a_response):
    return a_response()


@pytest.fixture
def a_response():
    def builder(text: str = "", status: int = 200):
        mock_response = Mock(ClientResponse)
        mock_response.status = status
        mock_response.text = AsyncMock(return_value=text)
        return mock_response

    return builder


class AsyncArgsMock(AsyncMock):
    def assert_awaited_once_with_args(self, **kwargs):
        self.assert_awaited_once()
        for keyword, value in kwargs.items():
            assert self.call_args.kwargs.get(keyword) == value
