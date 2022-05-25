import logging
from http import HTTPStatus
from logging import Logger
from typing import Callable
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import mark, fixture

from application.rpc import RpcLogger, RpcResponse, RpcRequest
from application.rpc.append_note_to_ticket_rpc import AppendNoteToTicketRpc, RequestBody


class TestAppendNoteToTicket:
    @mark.asyncio
    async def requests_are_properly_build_test(self, make_append_note_to_ticket_rpc):
        # given
        ticket_id = hash("any_ticket_id")
        note = "any_note"

        rpc = make_append_note_to_ticket_rpc()
        rpc.send = CoroutineMock()

        # when
        await rpc(ticket_id, note)

        # then
        rpc.send.assert_awaited_once_with(RpcRequest.construct(
            request_id=ANY,
            body=RequestBody(ticket_id=hash("any_ticket_id"), note="any_note")
        ))

    @mark.asyncio
    async def ok_responses_are_properly_handled_test(self, make_append_note_to_ticket_rpc):
        rpc = make_append_note_to_ticket_rpc()
        rpc.send = CoroutineMock(return_value=RpcResponse(status=HTTPStatus.OK))

        assert await rpc(hash("any_ticket_id"), "any_note")


@fixture
def make_append_note_to_ticket_rpc() -> Callable[..., AppendNoteToTicketRpc]:
    def builder(
        event_bus: EventBus = Mock(EventBus),
        logger: Logger = logging.getLogger(),
        timeout: int = hash("any_timeout"),
    ):
        rpc = AppendNoteToTicketRpc(event_bus, logger, timeout)
        rpc.start = Mock(return_value=(RpcRequest(request_id="a_request_id"), Mock(RpcLogger)))
        rpc.send = CoroutineMock()
        return rpc

    return builder
