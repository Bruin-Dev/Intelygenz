from logging import Logger
from typing import Dict, Any
from unittest.mock import Mock

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import fixture, mark

from application.rpc.base.rpc import Rpc
from application.rpc.base.rpc_request import RpcRequest
from application.rpc.base.rpc_response import RpcResponse


class TestRpc:
    def instance_test(self):
        # with patch.object('config'):
        event_bus, topic, timeout, logger = Mock(EventBus), Mock(str), Mock(int), Mock(Logger)

        subject = Rpc(event_bus, topic, timeout, logger)

        assert subject.event_bus == event_bus
        assert subject.topic == topic
        assert subject.timeout == timeout
        assert subject.logger == logger

    def requests_are_properly_initialized_test(self, base_rpc_builder):
        base_rpc = base_rpc_builder()

        subject_request_id, subject_logger = base_rpc.init_request()

        assert subject_request_id is not None
        assert isinstance(subject_request_id, str)
        assert subject_logger.extra.get("request_id") == subject_request_id

    @mark.asyncio
    async def responses_are_properly_returned_test(self, base_rpc_builder, an_rpc_request):
        # given
        status = 0
        body = Mock(Dict[str, Any])

        base_rpc = base_rpc_builder()
        base_rpc.event_bus.rpc_request = CoroutineMock(return_value={"status": status, "body": body})

        # when
        subject = await base_rpc.send(an_rpc_request)

        # then
        assert subject == RpcResponse(status=status, body=body)


@fixture
def an_rpc_request():
    return RpcRequest(request_id=Mock(str))


@fixture
def base_rpc_builder():
    def builder(
        event_bus: EventBus = Mock(EventBus),
        topic: str = Mock(str),
        timeout: int = Mock(int),
        logger: Logger = Mock(Logger)
    ):
        return Rpc(event_bus, topic, timeout, logger)

    return builder
