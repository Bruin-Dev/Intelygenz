from http import HTTPStatus
from typing import Callable
from unittest.mock import ANY, AsyncMock, Mock

from application.rpc import RpcFailedError, RpcResponse
from application.rpc.send_email_reply_rpc import RequestBody, SendEmailReplyRpc
from framework.nats.client import Client as NatsClient
from pytest import fixture, mark, raises


class TestSendEmailReplyRpc:
    @mark.asyncio
    async def requests_are_properly_built_test(self, make_send_email_rpc):
        parent_email_id = "any_parent_email_id"
        reply_body = "any_body"
        ok_response = RpcResponse(status=HTTPStatus.OK, body={"emailId": 1234})
        rpc = make_send_email_rpc()
        rpc.send = AsyncMock(return_value=ok_response)

        await rpc(parent_email_id, reply_body)

        rpc.send.assert_awaited_once_with(
            RequestBody.construct(
                request_id=ANY,
                body=RequestBody(parent_email_id=parent_email_id, reply_body=reply_body),
            )
        )

    @mark.asyncio
    async def responses_are_properly_parsed_test(self, make_send_email_rpc):
        rpc_response = RpcResponse(
            status=HTTPStatus.OK,
            body={"emailId": hash("any_email_id"), "historyId": hash("any_history_id"), "jobId": "any_job_id"},
        )
        rpc = make_send_email_rpc()
        rpc.send = AsyncMock(return_value=rpc_response)

        subject = await rpc("any_parent_email_id", "any_body")

        assert subject == str(hash("any_email_id"))

    @mark.asyncio
    async def unparseable_responses_raise_a_proper_exception_test(self, make_send_email_rpc):
        rpc_response = RpcResponse(status=HTTPStatus.OK, body="any_wrong_body")
        rpc = make_send_email_rpc()
        rpc.send = AsyncMock(return_value=rpc_response)

        with raises(RpcFailedError):
            await rpc("any_parent_email_id", "any_body")


@fixture
def make_send_email_rpc() -> Callable[..., SendEmailReplyRpc]:
    def builder(event_bus: NatsClient = Mock(NatsClient), timeout: int = hash("any_timeout")):
        return SendEmailReplyRpc(event_bus, timeout)

    return builder
