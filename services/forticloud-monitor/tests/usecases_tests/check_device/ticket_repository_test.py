from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError
from usecases_tests.check_device.data import AnyTicket, CustomException

from components import NatsClient
from usecases.check_device import Request, Settings, TicketRepository


async def tickets_are_properly_stored_test(repository_builder):
    # given
    request = AsyncMock()
    ticket_repository = repository_builder(request=request, settings=Settings(subject="any_subject"))

    # when
    await ticket_repository.store(AnyTicket(client_id="1", service_number="2"))

    # then
    request.assert_awaited_once_with("any_subject", Request(client_id=1, service_number=2))


async def wrong_data_storage_raises_an_exception_test(repository_builder):
    # given
    ticket_repository = repository_builder()

    # then
    with pytest.raises(ValidationError):
        await ticket_repository.store(AnyTicket(client_id="a", service_number="b"))


async def client_errors_are_properly_propagated_test(repository_builder):
    # given
    request = AsyncMock(side_effect=CustomException)
    ticket_repository = repository_builder(request=request)

    # then
    with pytest.raises(CustomException):
        await ticket_repository.store(AnyTicket())


@pytest.fixture
def repository_builder():
    def builder(request: AsyncMock = AsyncMock(), settings: Settings = Settings()):
        nats_client = NatsClient(Mock(), Mock())
        nats_client.request = request
        return TicketRepository(settings=settings, nats_client=nats_client)

    return builder
