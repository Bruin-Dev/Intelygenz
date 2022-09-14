from check_device_test.fixtures import AnyDevice, AnyDeviceId

from check_device.ticket import Ticket
from check_device.ticket_service import build_ticket_for


def tickets_are_properly_built_test():
    # given
    a_device_id = AnyDeviceId(client_id="any_client_id", service_number="any_service_number")
    a_device = AnyDevice(id=a_device_id)

    # when
    built_ticket = build_ticket_for(a_device)

    # then
    assert built_ticket == Ticket(client_id="any_client_id", service_number="any_service_number")
