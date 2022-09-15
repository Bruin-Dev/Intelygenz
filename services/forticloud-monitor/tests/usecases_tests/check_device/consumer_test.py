from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from conftest import CustomException, LoggerMock
from framework.nats.models import Subscription
from nats.aio.msg import Msg

from usecases.check_device import DeviceId, DeviceType
from usecases.check_device.consumer import Consumer, Settings

any_serialized_message = b'{"device_id":1,device_network_id":1,"client_id":1,"service_number":1,"type":"AP"}"'


def subcriptions_are_properly_built_test(consumer_builder):
    # given
    consumer = consumer_builder(settings=Settings(queue="any_queue", subject="any_subject"))

    # then
    assert consumer.subscription == Subscription(queue="any_queue", subject="any_subject", cb=consumer)


async def messages_are_properly_consumed_test(consumer_builder):
    # given
    usecase = AsyncMock()
    serialized_message = (
        b"{"
        b'"device_id":"any_id",'
        b'"device_network_id":1,'
        b'"client_id":true,'
        b'"service_number":"any_service_number",'
        b'"type":"AP"'
        b"}"
    )
    consumer = consumer_builder(usecase=usecase)

    # when
    await consumer(Msg(Mock(), data=serialized_message))

    # then
    expected_device_id = DeviceId(
        id="any_id",
        network_id="1",
        client_id="True",
        service_number="any_service_number",
        type=DeviceType.AP,
    )
    usecase.assert_awaited_once_with(expected_device_id)


@pytest.mark.parametrize(
    "serialized_message",
    [
        b"not_a_json_message",
        b'{id: "any_id"}',  # malformed json
        b'{"device_id": "any_id"}',  # missing fields
        b'{"type":"wrong_type","device_id":1,"device_network_id":1,"client_id":1,"service_number":1}',
    ],
)
async def parsing_errors_are_properly_reported_test(serialized_message: bytes, consumer_builder):
    # given
    exception = Mock()
    consumer = consumer_builder(logger=LoggerMock(exception=exception))

    # when
    await consumer(Msg(Mock(), data=serialized_message))

    # then
    exception.assert_called_once()


async def usecase_errors_are_properly_reported_test(consumer_builder):
    # given
    exception = Mock()
    consumer = consumer_builder(usecase=AsyncMock(side_effect=CustomException), logger=LoggerMock(exception=exception))

    # then
    await consumer(Msg(Mock(), data=any_serialized_message))

    # then
    exception.assert_called_once()


@pytest.fixture
def log():
    with mock.patch("usecases.check_device.consumer.log") as log:
        yield log


@pytest.fixture
def consumer_builder(log):
    def builder(
        usecase: AsyncMock = AsyncMock(),
        settings: Settings = Settings(),
        logger: LoggerMock = LoggerMock(),
    ):
        logger.configure(log)
        return Consumer(settings, usecase)

    return builder
