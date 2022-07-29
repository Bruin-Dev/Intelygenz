from http import HTTPStatus
from typing import Callable
from unittest.mock import ANY, AsyncMock, Mock

from application.rpc import RpcRequest, RpcResponse
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc, RequestBody
from framework.nats.client import Client as NatsClient
from pytest import fixture, mark


class TestAppendNoteToTicket:
    @mark.asyncio
    async def requests_are_properly_build_test(self, make_append_note_to_ticket_rpc):
        # given
        ticket_id = "any_ticket_id"
        note = "any_note"

        rpc = make_append_note_to_ticket_rpc()
        rpc.send = AsyncMock()

        # when
        await rpc(ticket_id, note)

        # then
        rpc.send.assert_awaited_once_with(
            RpcRequest.construct(request_id=ANY, body=RequestBody(ticket_id="any_ticket_id", note="any_note"))
        )

    @mark.asyncio
    async def ok_responses_are_properly_handled_test(self, make_append_note_to_ticket_rpc):
        rpc = make_append_note_to_ticket_rpc()
        rpc.send = AsyncMock(return_value=RpcResponse(status=HTTPStatus.OK))

        assert await rpc("any_ticket_id", "any_note")


@fixture
def make_append_note_to_ticket_rpc() -> Callable[..., AppendNoteToTicketRpc]:
    def builder(event_bus: NatsClient = Mock(NatsClient), timeout: int = hash("any_timeout")):
        return AppendNoteToTicketRpc(event_bus, timeout)

    return builder
