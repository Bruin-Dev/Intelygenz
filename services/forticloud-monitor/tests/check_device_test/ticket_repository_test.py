from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from check_device_test.fixtures import AnyTicket, CustomException
from pydantic import ValidationError

from check_device.nats_client import NatsClient
from check_device.ticket_repository import SUBJECT, Request, TicketRepository


async def requests_are_properly_built_test():
    # given
    a_client_id = str(hash("any_client_id"))
    a_service_number = str(hash("any_service_number"))
    a_ticket = AnyTicket(client_id=a_client_id, service_number=a_service_number)

    # when
    request = Request.build_from(a_ticket)

    # then
    assert request == Request(client_id=a_client_id, service_number=a_service_number)


async def wrong_data_requests_building_fail_test():
    # given
    a_ticket = AnyTicket(client_id="any_client_id", service_number="any_service_number")

    # then
    with pytest.raises(ValidationError):
        Request.build_from(a_ticket)


async def tickets_are_properly_stored_test(ticket_repository: TicketRepository, request_builder):
    # given
    a_request = AnyRequest()
    ticket_repository.nats_client.request = AsyncMock()
    request_builder.return_value = a_request

    # when
    await ticket_repository.store(AnyTicket())

    # then
    ticket_repository.nats_client.request.assert_awaited_once_with(SUBJECT, a_request, int)


async def client_errors_are_properly_propagated_test(ticket_repository: TicketRepository):
    # given
    ticket_repository.nats_client.request = AsyncMock(side_effect=CustomException)

    # then
    with pytest.raises(CustomException):
        await ticket_repository.store(AnyTicket())


class AnyRequest(Request):
    client_id: int = hash("any_client_id")
    service_number: int = hash("any_service_number")


@pytest.fixture
def ticket_repository() -> TicketRepository:
    return TicketRepository(Mock(NatsClient))


@pytest.fixture
def request_builder() -> Mock:
    with mock.patch("check_device.ticket_repository.Request.build_from") as build_from:
        yield build_from
