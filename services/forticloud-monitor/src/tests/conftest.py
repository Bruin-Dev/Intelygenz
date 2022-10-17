from datetime import datetime, timedelta

import pytest

from application.domain.device import Device, DeviceId, DeviceStatus, DeviceType
from application.domain.note import Note
from application.domain.service_number import ServiceNumber
from application.domain.task import TaskStatus, TicketTask
from application.domain.ticket import CreatedTicket, Ticket, TicketStatus


@pytest.fixture
def any_device_id():
    return DeviceId(
        id="any_id",
        network_id="any_network_id",
        client_id=str(hash("any_client_id")),
        service_number=ServiceNumber(str(hash("any_service_number"))),
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
def any_ticket():
    return Ticket(id="any_id", created_at=datetime.utcnow())


@pytest.fixture
def any_task():
    return TicketTask(
        id=str(hash("any_id")),
        service_number=ServiceNumber("any_service_number"),
        auto_resolution_grace_period=timedelta(minutes=90),
        max_auto_resolutions=3,
        status=TaskStatus.ONGOING,
        cycles=[],
    )


@pytest.fixture
def any_exception():
    class AnyException(Exception):
        pass

    return AnyException
