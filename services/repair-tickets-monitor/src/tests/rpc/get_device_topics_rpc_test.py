from logging import Logger
from typing import Dict, Any, Callable
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import fixture, mark, raises

from application.domain.device import Device
from application.domain.topic import Topic
from application.rpc.base.rpc_response import OK_STATUS, RpcResponse
from application.rpc.base_rpc import RpcLogger, RpcError
from application.rpc.get_device_topics_rpc import GetDeviceTopicsRpc, DeviceTopicsRequest, CallType, DeviceTopicsBody


class TestDeviceTopicsRequest:
    def instance_test(self):
        request_id = Mock(str)
        client_id = Mock(int)
        service_number = Mock(str)

        subject = DeviceTopicsRequest(request_id=request_id, client_id=client_id, service_number=service_number)

        assert subject.request_id == request_id
        assert subject.client_id == client_id
        assert subject.service_number == service_number

    def requests_are_properly_built_from_devices_test(self, a_device):
        request_id = Mock(str)
        subject = DeviceTopicsRequest.from_device(request_id=request_id, device=a_device)

        assert subject == DeviceTopicsRequest.construct(
            request_id=request_id,
            client_id=a_device.client_id,
            service_number=a_device.service_number
        )


class TestCallType:
    def instance_test(self):
        call_type = Mock(str)
        category = Mock(str)

        subject = CallType(callType=call_type, category=category)

        assert subject.call_type == call_type
        assert subject.category == category


class TestDeviceTopicsBody:
    def instance_test(self):
        call_types = []

        subject = DeviceTopicsBody(callTypes=call_types)

        assert subject.call_types == call_types

    def model_parses_only_valid_items_test(self):
        call_type = Mock(str)
        category = Mock(str)
        subject = DeviceTopicsBody.parse_obj({
            "callTypes": [
                {
                    "callType": call_type,
                    "category": category
                }, {
                    "callType": "any"
                }, {
                    "category": "any"
                },
                {},
                "non_dict_item",
            ]
        })

        assert subject.dict() == {
            "call_types": [{
                "call_type": call_type,
                "category": category
            }]
        }


class TestGetDeviceTopicsRpc:
    @mark.asyncio
    async def messages_are_properly_sent_test(self, get_device_topics_rpc_builder):
        # given
        client_id = Mock(int)
        service_number = Mock(str)
        call_type = Mock(str)
        category = Mock(str)

        device = Device(service_number=service_number, client_id=client_id)
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=RpcResponse(
            status=200,
            body={
                "callTypes": [{
                    "callType": call_type,
                    "category": category
                }]
            }
        ))

        # when
        subject = await get_device_topics_rpc(device)

        # then
        assert subject == [Topic(call_type=call_type, category=category)]
        get_device_topics_rpc.send.assert_awaited_once_with(
            DeviceTopicsRequest.construct(service_number=service_number, client_id=client_id, request_id=ANY)
        )

    @mark.asyncio
    async def exceptions_are_wrapped_test(
        self,
        get_device_topics_rpc_builder,
        a_device
    ):
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(side_effect=Exception)

        with raises(RpcError):
            await get_device_topics_rpc(a_device)


@fixture
def a_device() -> Device:
    return Device(service_number=Mock(str), client_id=Mock(int))


@fixture
def rpc_response_builder() -> Callable[..., RpcResponse]:
    def builder(
        status: int = OK_STATUS,
        body: Dict[str, Any] = Mock(dict)
    ):
        return RpcResponse(status, body)

    return builder


@fixture
def get_device_topics_rpc_builder() -> Callable[..., GetDeviceTopicsRpc]:
    def builder(
        event_bus: EventBus = Mock(EventBus),
        topic: str = Mock(str),
        timeout: int = Mock(int),
        logger: Logger = Mock(Logger)
    ):
        get_device_topics_rpc = GetDeviceTopicsRpc(event_bus, topic, timeout, logger)
        get_device_topics_rpc.start = Mock(return_value=(Mock(str), Mock(RpcLogger)))
        return get_device_topics_rpc

    return builder
