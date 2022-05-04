from logging import Logger
from typing import Dict, Any, Callable, Optional
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import fixture, mark, raises

from application.domain.device import Device
from application.domain.topic import Topic
from application.rpc.base_rpc import RpcLogger, RpcError, RpcResponse, OK_STATUS
from application.rpc.get_device_topics_rpc import GetDeviceTopicsRpc, DeviceTopicsRequest, DeviceTopicsBody


class TestDeviceTopicsRequest:
    def requests_are_properly_built_from_devices_test(self, a_device):
        request_id = "any_request_id"
        subject = DeviceTopicsRequest.from_device(request_id=request_id, device=a_device)

        assert subject == DeviceTopicsRequest(
            request_id=request_id,
            client_id=a_device.client_id,
            service_number=a_device.service_number
        )


class TestDeviceTopicsBody:
    def model_parses_only_valid_items_test(self):
        call_type = "any_call_type"
        category = "any_category"
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
    async def messages_are_properly_sent_test(self, get_device_topics_rpc_builder, a_device):
        # given
        call_type = "any_call_type"
        category = "any_category"

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
        subject = await get_device_topics_rpc(a_device)

        # then
        assert subject == [Topic(call_type=call_type, category=category)]
        get_device_topics_rpc.send.assert_awaited_once_with(
            DeviceTopicsRequest.construct(
                service_number=a_device.service_number,
                client_id=a_device.client_id,
                request_id=ANY
            )
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
    return Device(service_number="a_service_number", client_id=1)


@fixture
def rpc_response_builder() -> Callable[..., RpcResponse]:
    def builder(
        status: int = OK_STATUS,
        body: Optional[Dict[str, Any]] = None
    ):
        if body is None:
            body = {}

        return RpcResponse.construct(status=status, body=body)

    return builder


@fixture
def get_device_topics_rpc_builder() -> Callable[..., GetDeviceTopicsRpc]:
    def builder(
        event_bus: EventBus = Mock(EventBus),
        topic: str = "any_topic",
        timeout: int = 1,
        logger: Logger = Mock(Logger)
    ):
        get_device_topics_rpc = GetDeviceTopicsRpc(event_bus, topic, timeout, logger)
        get_device_topics_rpc.start = Mock(return_value=("a_request_id", Mock(RpcLogger)))
        return get_device_topics_rpc

    return builder
