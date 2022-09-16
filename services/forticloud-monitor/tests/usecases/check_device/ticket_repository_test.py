from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from clients import NatsClient
from usecases.check_device import Request, Settings, TicketRepository


async def tickets_are_properly_stored_test(repository_builder, any_ticket):
    # given
    any_ticket.client_id = "1"
    any_ticket.service_number = "2"
    request = AsyncMock()
    ticket_repository = repository_builder(request=request, settings=Settings(subject="any_subject"))

    # when
    await ticket_repository.store(any_ticket)

    # then
    request.assert_awaited_once_with("any_subject", Request(client_id=1, service_number=2))


async def wrong_data_storage_raises_an_exception_test(repository_builder, any_ticket):
    # given
    any_ticket.client_id = "a"
    ticket_repository = repository_builder()

    # then
    with pytest.raises(ValidationError):
        await ticket_repository.store(any_ticket)


async def client_errors_are_properly_propagated_test(repository_builder, any_ticket, any_exception):
    # given
    request = AsyncMock(side_effect=any_exception)
    ticket_repository = repository_builder(request=request)

    # then
    with pytest.raises(any_exception):
        await ticket_repository.store(any_ticket)


@pytest.fixture
def repository_builder():
    def builder(request: AsyncMock = AsyncMock(), settings: Settings = Settings()):
        nats_client = NatsClient(Mock(), Mock())
        nats_client.request = request
        return TicketRepository(nats_client, settings)

    return builder
