import pytest
from check_device_test.fixtures import AnyDevice

from check_device.ticket import Ticket
from check_device.ticket_service import TicketService


def tickets_are_properly_built_test(tickets_service: TicketService):
    # given
    a_device = AnyDevice()

    # when
    built_ticket = tickets_service.build_ticket_for(a_device)

    # then
    assert built_ticket == Ticket(client_id=a_device.id.client_id, service_number=a_device.id.service_number)


@pytest.fixture
def tickets_service() -> TicketService:
    return TicketService()
