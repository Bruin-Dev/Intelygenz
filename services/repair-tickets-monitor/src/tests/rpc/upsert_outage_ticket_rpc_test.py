from http import HTTPStatus
from typing import Callable
from unittest.mock import AsyncMock, Mock

from application.domain.asset import AssetId
from application.rpc import RpcError, RpcFailedError, RpcRequest, RpcResponse
from application.rpc.upsert_outage_ticket_rpc import (
    BRUIN_UPDATED_STATUS,
    MULTIPLE_CLIENTS_MSG,
    MULTIPLE_SITES_MSG,
    RequestBody,
    TicketContact,
    UpsertedStatus,
    UpsertedTicket,
    UpsertOutageTicketRpc,
)
from framework.nats.client import Client as NatsClient
from pytest import fixture, mark, raises


class TestUpsertOutageTicketRpc:
    @mark.asyncio
    async def tickets_are_properly_created_test(self, make_upsert_outage_ticket_rpc):
        # given
        client_id = "any_client_id"
        site_id = "any_site_id"
        contact_email = "any_contact_email"
        ticket_id = hash("any_ticket_id")
        asset_ids = [
            AssetId(client_id=client_id, site_id=site_id, service_number="service_number_1"),
            AssetId(client_id=client_id, site_id=site_id, service_number="service_number_2"),
        ]

        def side_effect(request: RpcRequest):
            if request.body == RequestBody(
                client_id=client_id,
                service_number={"service_number_1", "service_number_2"},
                ticket_contact=TicketContact(email=contact_email),
            ):
                return RpcResponse(status=HTTPStatus.OK, body=ticket_id)
            else:
                raise RpcFailedError(request=request, response=RpcResponse(status=HTTPStatus.BAD_REQUEST))

        rpc = make_upsert_outage_ticket_rpc()
        rpc.send = AsyncMock(side_effect=side_effect)

        subject = await rpc(asset_ids=asset_ids, contact_email=contact_email)

        # then
        assert subject == UpsertedTicket(status=UpsertedStatus.created, ticket_id=str(ticket_id))

    @mark.asyncio
    @mark.parametrize("bruin_updated_status", BRUIN_UPDATED_STATUS)
    async def tickets_are_properly_updated_test(self, make_upsert_outage_ticket_rpc, bruin_updated_status):
        # given
        client_id = "any_client_id"
        site_id = "any_site_id"
        contact_email = "any_contact_email"
        ticket_id = hash("any_ticket_id")
        asset_ids = [
            AssetId(client_id=client_id, site_id=site_id, service_number="service_number_1"),
            AssetId(client_id=client_id, site_id=site_id, service_number="service_number_2"),
        ]

        def side_effect(request: RpcRequest):
            if request.body == RequestBody(
                client_id=client_id,
                service_number={"service_number_1", "service_number_2"},
                ticket_contact=TicketContact(email=contact_email),
            ):
                raise RpcFailedError(request=request, response=RpcResponse(status=bruin_updated_status, body=ticket_id))
            else:
                raise RpcFailedError(request=request, response=RpcResponse(status=HTTPStatus.BAD_REQUEST))

        rpc = make_upsert_outage_ticket_rpc()
        rpc.send = AsyncMock(side_effect=side_effect)

        subject = await rpc(asset_ids=asset_ids, contact_email=contact_email)

        # then
        assert subject == UpsertedTicket(status=UpsertedStatus.updated, ticket_id=str(ticket_id))

    @mark.asyncio
    async def multiple_site_ids_raise_a_proper_error_test(self, make_upsert_outage_ticket_rpc, make_asset_id):
        rpc = make_upsert_outage_ticket_rpc()

        with raises(RpcError, match=MULTIPLE_SITES_MSG):
            await rpc(asset_ids=[make_asset_id(site_id="site_1"), make_asset_id(site_id="site_2")], contact_email="any")

    @mark.asyncio
    async def multiple_client_ids_raise_a_proper_error_test(self, make_upsert_outage_ticket_rpc, make_asset_id):
        rpc = make_upsert_outage_ticket_rpc()

        with raises(RpcError, match=MULTIPLE_CLIENTS_MSG):
            await rpc(
                asset_ids=[make_asset_id(client_id="client_1"), make_asset_id(client_id="client_2")],
                contact_email="any",
            )

    @mark.asyncio
    async def empty_bodies_raise_a_proper_error_test(self, make_upsert_outage_ticket_rpc, make_asset_id):
        # given
        rpc = make_upsert_outage_ticket_rpc()
        rpc.send = AsyncMock(return_value=RpcResponse(status=HTTPStatus.OK, body=None))

        with raises(RpcFailedError):
            await rpc(asset_ids=[make_asset_id()], contact_email="any")

    @mark.asyncio
    async def non_int_bodies_raise_a_proper_error_test(self, make_upsert_outage_ticket_rpc, make_asset_id):
        # given
        rpc = make_upsert_outage_ticket_rpc()
        rpc.send = AsyncMock(return_value=RpcResponse(status=HTTPStatus.OK, body="non_int"))

        with raises(RpcFailedError):
            await rpc(asset_ids=[make_asset_id()], contact_email="any")

    @mark.asyncio
    async def other_statuses_raise_a_proper_error_test(self, make_upsert_outage_ticket_rpc, make_asset_id):
        # given
        rpc = make_upsert_outage_ticket_rpc()
        rpc.send = AsyncMock(
            side_effect=RpcFailedError(
                request=RpcRequest.construct(), response=RpcResponse(status=HTTPStatus.BAD_REQUEST)
            )
        )

        with raises(RpcFailedError):
            await rpc(asset_ids=[make_asset_id()], contact_email="any")


@fixture
def make_upsert_outage_ticket_rpc() -> Callable[..., UpsertOutageTicketRpc]:
    def builder(
        event_bus: NatsClient = Mock(NatsClient),
        timeout: int = hash("any_timeout"),
    ):
        return UpsertOutageTicketRpc(event_bus, timeout)

    return builder
