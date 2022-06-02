from http import HTTPStatus
from logging import Logger
from typing import Callable
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import mark, raises, fixture

from application.rpc import RpcLogger, RpcError, RpcResponse, RpcRequest
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc, RequestBody


class TestAppendNoteToTicket:
    @mark.asyncio
    async def requests_are_properly_build_test(self, make_append_note_to_ticket_rpc):
        # given
        ticket_id = hash("any_ticket_id")
        note = "any_note"

        append_note_to_ticket_rpc = make_append_note_to_ticket_rpc()
        append_note_to_ticket_rpc.send = CoroutineMock()

        await append_note_to_ticket_rpc(ticket_id, note)

        # then
        append_note_to_ticket_rpc.send.assert_awaited_once_with(RpcRequest.construct(
            request_id=ANY,
            body=RequestBody(ticket_id=hash("any_ticket_id"), note="any_note")
        ))

    @mark.asyncio
    async def ok_responses_are_properly_handled_test(self, make_append_note_to_ticket_rpc):
        # given
        ticket_id = hash("any_ticket_id")
        note = "any_note"

        append_note_to_ticket_rpc = make_append_note_to_ticket_rpc()
        append_note_to_ticket_rpc.send = CoroutineMock(return_value=RpcResponse(status=HTTPStatus.OK))

        # then
        assert await append_note_to_ticket_rpc(ticket_id, note)

    @mark.asyncio
    async def ko_responses_are_properly_handled_test(self, make_append_note_to_ticket_rpc):
        append_note_to_ticket_rpc = make_append_note_to_ticket_rpc()
        append_note_to_ticket_rpc.send = CoroutineMock(return_value=RpcResponse(status=HTTPStatus.BAD_REQUEST))

        assert not await append_note_to_ticket_rpc(hash("any_ticket_id"), "any_note")

    @mark.asyncio
    async def exceptions_are_properly_wrapped_test(self, make_append_note_to_ticket_rpc):
        append_note_to_ticket_rpc = make_append_note_to_ticket_rpc()
        append_note_to_ticket_rpc.send = CoroutineMock(side_effect=Exception)

        with raises(RpcError):
            await append_note_to_ticket_rpc(hash("any_ticket_id"), "any_note")


@fixture
def make_append_note_to_ticket_rpc() -> Callable[..., AppendNoteToTicketRpc]:
    def builder(
        event_bus: EventBus = Mock(EventBus),
        logger: Logger = Mock(Logger),
        timeout: int = hash("any_timeout"),
    ):
        append_note_to_ticket_rpc = AppendNoteToTicketRpc(event_bus, logger, timeout)
        append_note_to_ticket_rpc.start = Mock(return_value=(RpcRequest(request_id="a_request_id"), Mock(RpcLogger)))
        append_note_to_ticket_rpc.send = CoroutineMock()
        return append_note_to_ticket_rpc

    return builder
