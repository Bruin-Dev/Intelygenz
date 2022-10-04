from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from framework.nats.models import Subscription
from nats.aio.msg import Msg

from application.consumers import ApConsumer, ConsumerSettings
from application.models.device import DeviceId, DeviceType

any_serialized_message = b'{"device_id":1,device_network_id":1,"client_id":1,"service_number":1}'


def subcriptions_are_properly_built_test(any_switch_consumer):
    # given
    consumer = any_switch_consumer(settings=ConsumerSettings(queue="any_queue", subject="any_subject"))

    # then
    assert consumer.subscription() == Subscription(queue="any_queue", subject="any_subject", cb=consumer)


async def messages_are_properly_consumed_test(any_switch_consumer):
    # given
    check_device = AsyncMock()
    serialized_message = (
        b"{"
        b'"device_id":"any_id",'
        b'"device_network_id":1,'
        b'"client_id":true,'
        b'"service_number":"any_service_number"'
        b"}"
    )
    consumer = any_switch_consumer(check_device=check_device)

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
    check_device.assert_awaited_once_with(expected_device_id)


@pytest.mark.parametrize(
    "serialized_message",
    [
        b"not_a_json_message",
        b'{id: "any_id"}',
        b'{"device_id": "any_id"}',
        b'{"device_id":{},"device_network_id":1,"client_id":1,"service_number":1}',
    ],
    ids=[
        "not a json message",
        "malformed json",
        "missing fields",
        "wrong device_id type",
    ],
)
async def parsing_errors_are_properly_reported_test(serialized_message: bytes, any_switch_consumer):
    # given
    exception_log = Mock()
    consumer = any_switch_consumer(exception_log=exception_log)

    # when
    await consumer(Msg(Mock(), data=serialized_message))

    # then
    exception_log.assert_called_once()


async def check_device_errors_are_properly_reported_test(any_switch_consumer, any_exception):
    # given
    exception_log = Mock()
    consumer = any_switch_consumer(check_device=AsyncMock(side_effect=any_exception), exception_log=exception_log)

    # then
    await consumer(Msg(Mock(), data=any_serialized_message))

    # then
    exception_log.assert_called_once()


@pytest.fixture
def log():
    with mock.patch("application.consumers.ap_consumer.log") as log:
        yield log


@pytest.fixture
def any_switch_consumer(log, any_settings):
    def builder(
        check_device: AsyncMock = AsyncMock(),
        settings: ConsumerSettings = any_settings,
        exception_log: Mock = Mock(),
    ):
        log.exception = exception_log
        return ApConsumer(settings, check_device)

    return builder


@pytest.fixture
def any_settings():
    return ConsumerSettings(queue="any_queue", subject="any_subject")
