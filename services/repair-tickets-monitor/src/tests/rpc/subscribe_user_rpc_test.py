from http import HTTPStatus
from typing import Callable
from unittest.mock import ANY, AsyncMock, Mock

from framework.nats.client import Client as NatsClient
from pytest import fixture, mark, raises

from application.rpc import RpcFailedError, RpcRequest, RpcResponse
from application.rpc.subscribe_user_rpc import SUBSCRIPTION_TYPE, RequestBody, SubscribeUserRpc


class TestSubscribeUserRpc:
    @mark.asyncio
    async def requests_are_properly_build_test(self, make_subscribe_user_rpc):
        # given
        ticket_id = "any_ticket_id"
        user_email = "any_user_email"

        rpc = make_subscribe_user_rpc()
        rpc.send = AsyncMock()

        await rpc(ticket_id, user_email)

        # then
        rpc.send.assert_awaited_once_with(
            RpcRequest.construct(
                request_id=ANY,
                body=RequestBody(ticket_id=ticket_id, user_email=user_email, subscription_type=SUBSCRIPTION_TYPE),
            )
        )

    @mark.asyncio
    async def ok_responses_are_properly_handled_test(self, make_subscribe_user_rpc):
        rpc = make_subscribe_user_rpc()
        rpc.send = AsyncMock(return_value=RpcResponse(status=HTTPStatus.OK))

        assert await rpc("any_ticket_id", "any_user_email")

    @mark.asyncio
    async def forbidden_responses_are_properly_handled_test(self, make_subscribe_user_rpc):
        forbidden_error = RpcFailedError(
            request=RpcRequest.construct(), response=RpcResponse(status=HTTPStatus.FORBIDDEN)
        )

        rpc = make_subscribe_user_rpc()
        rpc.send = AsyncMock(side_effect=forbidden_error)

        assert not await rpc("any_ticket_id", "any_user_email")

    @mark.asyncio
    async def internal_service_error_responses_are_properly_handled_test(self, make_subscribe_user_rpc):
        internal_server_error = RpcFailedError(
            request=RpcRequest.construct(), response=RpcResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        )

        rpc = make_subscribe_user_rpc()
        rpc.send = AsyncMock(side_effect=internal_server_error)

        assert not await rpc("any_ticket_id", "any_user_email")

    @mark.asyncio
    async def other_error_responses_are_properly_raised_test(self, make_subscribe_user_rpc):
        other_error = RpcFailedError(
            request=RpcRequest.construct(), response=RpcResponse(status=HTTPStatus.BAD_REQUEST)
        )

        rpc = make_subscribe_user_rpc()
        rpc.send = AsyncMock(side_effect=other_error)

        with raises(RpcFailedError):
            await rpc("any_ticket_id", "any_user_email")


@fixture
def make_subscribe_user_rpc() -> Callable[..., SubscribeUserRpc]:
    def builder(event_bus: NatsClient = Mock(NatsClient), timeout: int = hash("any_timeout")):
        return SubscribeUserRpc(event_bus, timeout)

    return builder
