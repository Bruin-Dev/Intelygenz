import logging
from http import HTTPStatus
from logging import Logger
from typing import Callable, Set
from unittest.mock import ANY, AsyncMock, Mock

from framework.nats.client import Client as NatsClient
from pydantic import BaseModel
from pytest import fixture, mark, raises

from application.rpc import Rpc, RpcError, RpcFailedError, RpcLogger, RpcRequest, RpcResponse


class SetRpcBody(BaseModel):
    set: Set[str]


class TestRpc:
    def requests_are_properly_started_test(self, make_rpc):
        rpc = make_rpc()

        subject_request, subject_logger = rpc.start()

        assert subject_request is not None
        assert subject_request == RpcRequest.construct(request_id=ANY)
        assert subject_logger.extra.get("request_id") == subject_request.request_id

    @mark.asyncio
    async def sets_are_properly_serialized_test(self, make_rpc, make_msg):
        rpc = make_rpc()
        rpc._nats_client.request = AsyncMock(return_value=make_msg({"status": HTTPStatus.OK}))
        rpc_request = RpcRequest(request_id="any", body=SetRpcBody(set={"any_value"}))

        await rpc.send(rpc_request)

        rpc._nats_client.request.assert_awaited_once_with(
            subject=ANY,
            payload='{"request_id":"any","body":{"set":["any_value"]}}'.encode(),
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


class TestRpcLogger:
    def messages_are_properly_formatted_test(self, make_rpc_logger):
        kwargs = Mock()
        rpc_logger = make_rpc_logger(request_id="any_request_id")

        subject_message, subject_kwargs = rpc_logger.process("any_message", kwargs)

        assert subject_message == "[request_id=any_request_id] any_message"


@fixture
def any_rpc_request() -> RpcRequest:
    return RpcRequest(request_id="any_request_id")


@fixture
def make_rpc_logger() -> Callable[..., RpcLogger]:
    def builder(logger: Logger = logging.getLogger(), request_id: str = "any_request_id"):
        return RpcLogger(logger, request_id)

    return builder


@fixture
def make_rpc() -> Callable[..., Rpc]:
    def builder(
        event_bus: NatsClient = Mock(NatsClient),
        logger: Logger = logging.getLogger(),
        topic: str = "any_topic",
        timeout: int = hash("any_timeout"),
    ):
        return Rpc(event_bus, logger, topic, timeout)

    return builder
