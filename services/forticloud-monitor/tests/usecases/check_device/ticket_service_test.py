from usecases.check_device import Ticket, build_ticket_for


def tickets_are_properly_built_test(any_device):
    # given
    any_device.id.client_id = "any_client_id"
    any_device.id.service_number = "any_service_number"

    # when
    built_ticket = build_ticket_for(any_device)

    # then
    assert built_ticket == Ticket(client_id="any_client_id", service_number="any_service_number")
