from unittest.mock import AsyncMock, Mock

import pytest

from shared import NatsClient
from usecases.check_device import StoreTicket, StoreTicketSettings


async def tickets_are_properly_stored_test(scenario, any_ticket):
    pass
    # # given
    # any_ticket.client_id = "1"
    # any_ticket.service_number = "2"
    # request = AsyncMock()
    # store_ticket = scenario(request=request, settings=StoreTicketSettings(subject="any_subject"))
    #
    # # when
    # await store_ticket(any_ticket)
    #
    # # then
    # request.assert_awaited_once_with("any_subject", Request(client_id=1, service_number=2))


async def wrong_data_storage_raises_an_exception_test(scenario, any_ticket):
    pass
    # # given
    # any_ticket.client_id = "a"
    # store_ticket = scenario()
    #
    # # then
    # with pytest.raises(ValidationError):
    #     await store_ticket(any_ticket)


async def client_errors_are_properly_propagated_test(scenario, any_ticket, any_exception):
    pass
    # # given
    # request = AsyncMock(side_effect=any_exception)
    # store_ticket = scenario(request=request)
    #
    # # then
    # with pytest.raises(any_exception):
    #     await store_ticket(any_ticket)


@pytest.fixture
def scenario(any_store_ticket_settings):
    def builder(request: AsyncMock = AsyncMock(), settings: StoreTicketSettings = any_store_ticket_settings):
        nats_client = NatsClient(Mock(), Mock())
        nats_client.request = request
        return StoreTicket(settings, nats_client)

    return builder


@pytest.fixture
def any_store_ticket_settings():
    return StoreTicketSettings()
