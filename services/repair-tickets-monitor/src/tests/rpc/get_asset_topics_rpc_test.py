from http import HTTPStatus
from typing import Callable
from unittest.mock import ANY, AsyncMock, Mock

from framework.nats.client import Client as NatsClient
from pytest import fixture, mark, raises

from application.domain.asset import Topic
from application.rpc import RpcFailedError, RpcResponse
from application.rpc.get_asset_topics_rpc import GetAssetTopicsRpc, RequestBody


class TestGetAssetTopicsRpc:
    @mark.asyncio
    async def requests_are_properly_built_test(self, make_get_asset_topics_rpc, make_asset_id):
        ok_response = RpcResponse(status=HTTPStatus.OK, body={"callTypes": []})
        any_asset_id = make_asset_id()
        rpc = make_get_asset_topics_rpc()
        rpc.send = AsyncMock(return_value=ok_response)

        await rpc(any_asset_id)

        rpc.send.assert_awaited_once_with(
            RequestBody.construct(
                request_id=ANY,
                body=RequestBody(client_id=any_asset_id.client_id, service_number=any_asset_id.service_number),
            )
        )

    @mark.asyncio
    async def responses_are_properly_parsed_test(self, make_get_asset_topics_rpc, make_asset_id):
        rpc_response = RpcResponse(
            status=HTTPStatus.OK,
            body={
                "callTypes": [
                    {"callType": "any_call_type", "category": "any_category"},
                    {"callType": "anything"},
                    {"category": "anything"},
                    {},
                    "non_dict_item",
                ]
            },
        )
        rpc = make_get_asset_topics_rpc()
        rpc.send = AsyncMock(return_value=rpc_response)

        subject = await rpc(make_asset_id())

        assert subject == [Topic(call_type="any_call_type", category="any_category")]

    @mark.asyncio
    async def unparseable_responses_raise_a_proper_exception_test(self, make_get_asset_topics_rpc, make_asset_id):
        rpc_response = RpcResponse(status=HTTPStatus.OK, body="any_wrong_body")
        rpc = make_get_asset_topics_rpc()
        rpc.send = AsyncMock(return_value=rpc_response)

        with raises(RpcFailedError):
            await rpc(make_asset_id())


@fixture
def make_get_asset_topics_rpc() -> Callable[..., GetAssetTopicsRpc]:
    def builder(event_bus: NatsClient = Mock(NatsClient), timeout: int = hash("any_timeout")):
        return GetAssetTopicsRpc(event_bus, timeout)

    return builder
