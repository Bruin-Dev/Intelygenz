from logging import Logger
from unittest.mock import Mock

from pytest import fixture

from application.rpc.base.rpc_logger import RpcLogger


class TestRpcLogger:
    def instance_test(self):
        logger = Mock(Logger)
        request_id = Mock(str)

        subject = RpcLogger(logger, request_id)

        assert subject.extra.get("request_id") == request_id
        assert subject.logger == logger

    def messages_are_properly_formatted_test(self, rpc_logger_builder):
        kwargs = Mock()
        rpc_logger = rpc_logger_builder(request_id="a_request_id")

        subject_message, subject_kwargs = rpc_logger.process("a_message", kwargs)

        assert subject_message == "[request_id=a_request_id] a_message"


@fixture
def rpc_logger_builder():
    def builder(logger: Logger = Mock(Logger), request_id: str = Mock(str)):
        return RpcLogger(logger, request_id)

    return builder
