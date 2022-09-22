from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from framework.nats.models import Subscription
from nats.aio.msg import Msg

from usecases.check_device import DeviceConsumer, DeviceConsumerSettings, DeviceId, DeviceType

any_serialized_message = b'{"device_id":1,device_network_id":1,"client_id":1,"service_number":1,"type":"AP"}"'


def subcriptions_are_properly_built_test(scenario):
    # given
    consumer = scenario(settings=DeviceConsumerSettings(queue="any_queue", subject="any_subject"))

    # then
    assert consumer.subscription() == Subscription(queue="any_queue", subject="any_subject", cb=consumer)


async def messages_are_properly_consumed_test(scenario):
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
    consumer = scenario(usecase=usecase)

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
async def parsing_errors_are_properly_reported_test(serialized_message: bytes, scenario):
    # given
    exception_log = Mock()
    consumer = scenario(exception_log=exception_log)

    # when
    await consumer(Msg(Mock(), data=serialized_message))

    # then
    exception_log.assert_called_once()


async def usecase_errors_are_properly_reported_test(scenario, any_exception):
    # given
    exception_log = Mock()
    consumer = scenario(usecase=AsyncMock(side_effect=any_exception), exception_log=exception_log)

    # then
    await consumer(Msg(Mock(), data=any_serialized_message))

    # then
    exception_log.assert_called_once()


@pytest.fixture
def log():
    with mock.patch("usecases.check_device.device_consumer.log") as log:
        yield log


@pytest.fixture
def scenario(log, any_settings):
    def builder(
        usecase: AsyncMock = AsyncMock(),
        settings: DeviceConsumerSettings = any_settings,
        exception_log: Mock = Mock(),
    ):
        log.exception = exception_log
        return DeviceConsumer(settings, usecase)

    return builder


@pytest.fixture
def any_settings():
    return DeviceConsumerSettings(queue="any_queue", subject="any_subject")
