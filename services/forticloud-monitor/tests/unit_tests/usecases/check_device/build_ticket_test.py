import pytest

from usecases.check_device import BuildTicket, Ticket


def tickets_are_properly_built_test(scenario, any_device):
    # given
    build_ticket = scenario()
    any_device.id.client_id = "any_client_id"
    any_device.id.service_number = "any_service_number"

    # when
    built_ticket = build_ticket(any_device)

    # then
    assert built_ticket == Ticket(client_id="any_client_id", service_number="any_service_number")


@pytest.fixture()
def scenario():
    def builder():
        return BuildTicket()

    return builder
