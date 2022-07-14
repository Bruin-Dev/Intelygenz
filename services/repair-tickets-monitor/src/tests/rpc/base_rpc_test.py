from http import HTTPStatus
from typing import Callable, Dict, List, Set
from unittest.mock import ANY, AsyncMock, Mock

from framework.nats.client import Client as NatsClient
from pydantic import BaseModel
from pytest import fixture, mark, raises

from application.rpc import Rpc, RpcError, RpcFailedError, RpcRequest, RpcResponse


class FooObject(BaseModel):
    str: str
    int: int
    float: float
    bool: bool


class FooBody(BaseModel):
    set: Set[str]
    list: List[str]
    map: Dict[str, FooObject]


class TestRpc:
    @mark.asyncio
    async def requests_are_properly_serialized_test(self, make_rpc, make_msg):
        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": HTTPStatus.OK}))
        body = FooBody(
            set={"any_set_item"},
            list=["any_list_item"],
            map={"key": FooObject(str="any_string", int=1, float=1.0, bool=True)},
        )
        rpc_request = RpcRequest(request_id="any", body=body)

        await rpc.send(rpc_request)

        expected_payload = (
            "{"
            '"request_id":"any",'
            '"body":{'
            '"set":["any_set_item"],'
            '"list":["any_list_item"],'
            '"map":{"key":{"str":"any_string","int":1,"float":1.0,"bool":true}}'
            "}}"
        )
        rpc._nats_client.request.assert_awaited_once_with(
            subject=ANY,
            payload=expected_payload.encode(),
            timeout=ANY,
        )

    @mark.asyncio
    async def responses_are_properly_parsed_test(self, make_rpc, make_msg, any_rpc_request):
        # given
        status = HTTPStatus.OK
        body = "any"

        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": status, "body": body}))

        # when
        subject = await rpc.send(any_rpc_request)

        # then
        assert subject == RpcResponse(status=status, body=body)

    @mark.asyncio
    async def no_body_responses_are_properly_parsed_test(self, make_rpc, make_msg, any_rpc_request):
        # given
        status = HTTPStatus.OK

        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": status}))

        # when
        subject = await rpc.send(any_rpc_request)

        # then
        assert subject == RpcResponse(status=status)

    @mark.asyncio
    async def failing_requests_raise_a_proper_error_test(self, make_rpc, any_rpc_request):
        base_rpc = make_rpc()
        base_rpc._nats_client.request = AsyncMock(side_effect=Exception)

        with raises(RpcError):
            await base_rpc.send(any_rpc_request)

    @mark.asyncio
    async def none_responses_raise_a_proper_error_test(self, make_rpc, make_msg, any_rpc_request):
        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg(None))

        with raises(RpcError):
            await rpc.send(any_rpc_request)

    @mark.asyncio
    async def non_parseable_responses_raise_a_proper_error_test(self, make_rpc, make_msg, any_rpc_request):
        base_rpc = make_rpc()
        base_rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": "non_numeric_status", "body": {}}))

        with raises(RpcError):
            await base_rpc.send(any_rpc_request)

    @mark.asyncio
    async def non_status_responses_raise_a_proper_error_test(self, make_rpc, make_msg, any_rpc_request):
        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg({"body": {}}))

        with raises(RpcError):
            await rpc.send(any_rpc_request)

    @mark.asyncio
    async def non_ok_responses_raise_a_proper_error_test(self, make_rpc, make_msg, any_rpc_request):
        base_rpc = make_rpc()
        base_rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": HTTPStatus.BAD_REQUEST}))

        with raises(RpcFailedError):
            await base_rpc.send(any_rpc_request)


class TestRpcResponse:
    def ok_response_are_properly_detected_test(self):
        assert RpcResponse(status=HTTPStatus.OK, body={}).is_ok()

    def ko_response_are_properly_detected_test(self):
        assert not RpcResponse(status=HTTPStatus.BAD_REQUEST, body={}).is_ok()


@fixture
def any_rpc_request() -> RpcRequest:
    return RpcRequest(request_id="any_request_id")


@fixture
def make_rpc() -> Callable[..., Rpc]:
    def builder(
        event_bus: NatsClient = Mock(NatsClient),
        topic: str = "any_topic",
        timeout: int = hash("any_timeout"),
    ):
        return Rpc(event_bus, topic, timeout)

    return builder
