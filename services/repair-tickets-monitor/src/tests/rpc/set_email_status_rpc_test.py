from typing import Callable
from unittest.mock import ANY, AsyncMock, Mock

from application.domain.email import EmailStatus
from application.rpc import RpcRequest
from application.rpc.set_email_status_rpc import RequestBody, SetEmailStatusRpc
from framework.nats.client import Client as NatsClient
from pytest import fixture, mark


class TestSubscribeUserRpc:
    @mark.asyncio
    @mark.parametrize(
        "email_status, serialized_status",
        [
            (EmailStatus.NEW, "New"),
            (EmailStatus.AIQ, "AIQ"),
            (EmailStatus.DONE, "Done"),
        ],
    )
    async def requests_are_properly_build_test(self, make_set_email_status_rpc, email_status, serialized_status):
        # given
        email_id = "email_id"

        rpc = make_set_email_status_rpc()
        rpc.send = AsyncMock()

        await rpc(email_id, email_status)

        # then
        rpc.send.assert_awaited_once_with(
            RpcRequest.construct(
                request_id=ANY,
                body=RequestBody(email_id=email_id, email_status=serialized_status),
            )
        )


@fixture
def make_set_email_status_rpc() -> Callable[..., SetEmailStatusRpc]:
    def builder(event_bus: NatsClient = Mock(NatsClient), timeout: int = hash("any_timeout")):
        return SetEmailStatusRpc(event_bus, timeout)

    return builder
