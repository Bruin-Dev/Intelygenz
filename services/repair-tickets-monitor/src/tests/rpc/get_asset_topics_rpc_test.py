from logging import Logger
from typing import Dict, Any, Callable, Optional
from unittest.mock import Mock, ANY

from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus
from pytest import fixture, mark, raises

from application.domain.asset import AssetId, Topic
from application.rpc import RpcLogger, RpcError, RpcResponse, OK_STATUS, RpcRequest
from application.rpc.get_asset_topics_rpc import GetAssetTopicsRpc, RequestBody


class TestGetAssetTopicsRpc:
    @mark.asyncio
    async def requests_are_properly_built_test(self, make_get_asset_topics_rpc, any_device_id):
        get_asset_topics_rpc = make_get_asset_topics_rpc()
        get_asset_topics_rpc.send = CoroutineMock()

        await get_asset_topics_rpc(any_device_id)

        get_asset_topics_rpc.send.assert_awaited_once_with(RequestBody.construct(
            request_id=ANY,
            body=RequestBody(
                client_id=any_device_id.client_id,
                service_number=any_device_id.service_number
            )
        ))

    @mark.asyncio
    async def ok_responses_are_properly_parsed_test(self, make_get_asset_topics_rpc, any_device_id):
        rpc_response = RpcResponse(
            status=200,
            body={
                "callTypes": [
                    {
                        "callType": "any_call_type",
                        "category": "any_category"
                    }, {
                        "callType": "anything"
                    }, {
                        "category": "anything"
                    },
                    {},
                    "non_dict_item",
                ]
            })
        get_asset_topics_rpc = make_get_asset_topics_rpc()
        get_asset_topics_rpc.send = CoroutineMock(return_value=rpc_response)

        subject = await get_asset_topics_rpc(any_device_id)

        assert subject == [Topic(call_type="any_call_type", category="any_category")]

    @mark.asyncio
    async def unparseable_responses_are_properly_handled_test(self, make_get_asset_topics_rpc, any_device_id):
        rpc_response = RpcResponse(status=200, body="any_wrong_body")
        get_asset_topics_rpc = make_get_asset_topics_rpc()
        get_asset_topics_rpc.send = CoroutineMock(return_value=rpc_response)

        subject = await get_asset_topics_rpc(any_device_id)

        assert subject == []

    @mark.asyncio
    async def ko_responses_are_properly_handled_test(self, make_get_asset_topics_rpc, any_device_id):
        rpc_response = RpcResponse(
            status=400,
            body={
                "errorMessage": "any_error_message",
                "errorCode": "any_error_code"
            })
        get_asset_topics_rpc = make_get_asset_topics_rpc()
        get_asset_topics_rpc.send = CoroutineMock(return_value=rpc_response)

        subject = await get_asset_topics_rpc(any_device_id)

        assert subject == []

    @mark.asyncio
    async def exceptions_are_properly_wrapped_test(
        self,
        make_get_asset_topics_rpc,
        any_device_id
    ):
        get_asset_topics_rpc = make_get_asset_topics_rpc()
        get_asset_topics_rpc.send = CoroutineMock(side_effect=Exception)

        with raises(RpcError):
            await get_asset_topics_rpc(any_device_id)


@fixture
def any_device_id() -> AssetId:
    return AssetId(
        service_number="any_service_number",
        client_id=hash("any_client_id"),
        site_id=hash("any_site_id")
    )


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
def make_get_asset_topics_rpc() -> Callable[..., GetAssetTopicsRpc]:
    def builder(
        event_bus: EventBus = Mock(EventBus),
        logger: Logger = Mock(Logger),
        timeout: int = hash("any_timeout")
    ):
        get_asset_topics_rpc = GetAssetTopicsRpc(event_bus, logger, timeout)
        get_asset_topics_rpc.start = Mock(return_value=(RpcRequest(request_id="a_request_id"), Mock(RpcLogger)))
        return get_asset_topics_rpc

    return builder
