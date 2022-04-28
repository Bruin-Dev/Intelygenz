from logging import Logger
from typing import Dict, Any
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from pytest import fixture, mark

from application.domain.device import Device
from application.domain.topic import Topic
from application.rpc.base.rpc_response import OK_STATUS, RpcResponse
from application.rpc.get_device_topics_rpc import GetDeviceTopicsRpc, DeviceTopicsRequest


class TestGetDeviceTopicsRpc:
    @mark.asyncio
    async def messages_are_properly_sent_test(self, get_device_topics_rpc_builder):
        # given
        client_id = Mock(int)
        service_number = Mock(str)

        device = Device(service_number=service_number, client_id=client_id)
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock()

        # when
        await get_device_topics_rpc.get_topics_for(device)

        # then
        get_device_topics_rpc.send.assert_awaited_once_with(
            DeviceTopicsRequest(service_number=service_number, client_id=client_id, request_id=ANY)
        )

    @mark.asyncio
    async def responses_are_properly_mapped_test(self, get_device_topics_rpc_builder, rpc_response_builder, a_device):
        # given
        call_type = Mock(str)
        category = Mock(str)

        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=rpc_response_builder(
            body={
                "callTypes": [{
                    "callType": call_type,
                    "category": category,
                }]
            }
        ))

        # when
        subject = await get_device_topics_rpc.get_topics_for(a_device)

        # then
        assert subject == [Topic(call_type=call_type, category=category)]

    @mark.asyncio
    async def empty_body_responses_are_properly_mapped_test(
        self,
        get_device_topics_rpc_builder,
        rpc_response_builder,
        a_device,
    ):
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=rpc_response_builder(body={}))

        subject = await get_device_topics_rpc.get_topics_for(a_device)

        assert subject == []

    @mark.asyncio
    async def non_dict_items_are_properly_mapped_test(
        self,
        get_device_topics_rpc_builder,
        rpc_response_builder,
        a_device
    ):
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=rpc_response_builder(body={
            "callTypes": ["non_dict_call_type"]
        }))

        subject = await get_device_topics_rpc.get_topics_for(a_device)

        assert subject == []

    @mark.asyncio
    async def missing_call_type_items_are_properly_mapped_test(
        self,
        get_device_topics_rpc_builder,
        rpc_response_builder,
        a_device
    ):
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=rpc_response_builder(body={
            "callTypes": [{"category": Mock(str)}]
        }))

        subject = await get_device_topics_rpc.get_topics_for(a_device)

        assert subject == []

    @mark.asyncio
    async def missing_category_items_are_properly_mapped_test(
        self,
        get_device_topics_rpc_builder,
        rpc_response_builder,
        a_device
    ):
        get_device_topics_rpc = get_device_topics_rpc_builder()
        get_device_topics_rpc.send = CoroutineMock(return_value=rpc_response_builder(body={
            "callTypes": [{"callType": Mock(str)}]
        }))

        subject = await get_device_topics_rpc.get_topics_for(a_device)

        assert subject == []


@fixture
def rpc_response_builder():
    def builder(
        status: int = OK_STATUS,
        body: Dict[str, Any] = Mock(dict)
    ):
        return RpcResponse(status, body)

    return builder


@fixture
def a_device():
    return Device(service_number=Mock(str), client_id=Mock(int))


@fixture
def get_device_topics_rpc_builder():
    def builder(
        event_bus: EventBus = Mock(EventBus),
        topic: str = Mock(str),
        timeout: int = Mock(int),
        logger_client: LoggerClient = Mock(LoggerClient)
    ):
        get_device_topics_rpc = GetDeviceTopicsRpc(event_bus, topic, timeout, logger_client)
        get_device_topics_rpc.init_request = Mock(return_value=(Mock(str), Mock(Logger)))
        return get_device_topics_rpc

    return builder
