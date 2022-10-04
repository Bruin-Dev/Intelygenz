import pytest

from application.models.device import Device, DeviceId, DeviceStatus, DeviceType
from application.models.note import Note
from application.models.ticket import CreatedTicket, TicketStatus


@pytest.fixture
def any_device_id():
    return DeviceId(
        id="any_id",
        network_id="any_network_id",
        client_id=str(hash("any_client_id")),
        service_number=str(hash("any_service_number")),
        type=DeviceType.AP,
    )


@pytest.fixture
def any_device(any_device_id):
    return Device(id=any_device_id, status=DeviceStatus.ONLINE, name="any_name", type="any_type", serial="any_serial")


@pytest.fixture
def any_online_device(any_device):
    any_device.status = DeviceStatus.ONLINE
    return any_device


@pytest.fixture
def any_offline_device(any_device):
    any_device.status = DeviceStatus.OFFLINE
    return any_device


@pytest.fixture
def any_created_ticket():
    return CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.CREATED)


@pytest.fixture
def any_note():
    return Note(ticket_id="any_ticket_id", service_number="any_service_number", text="any_text")


@pytest.fixture
def any_in_progress_ticket_status():
    return TicketStatus.REOPENED_SAME_LOCATION


@pytest.fixture
def any_exception():
    class AnyException(Exception):
        pass

    return AnyException
