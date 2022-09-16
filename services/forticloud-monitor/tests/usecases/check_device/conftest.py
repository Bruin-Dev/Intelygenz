import pytest

from usecases.check_device import Device, DeviceId, DeviceStatus, DeviceType, Ticket


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
    return Device(id=any_device_id, status=DeviceStatus.ONLINE)


@pytest.fixture
def any_online_device(any_device):
    any_device.status = DeviceStatus.ONLINE
    return any_device


@pytest.fixture
def any_offline_device(any_device):
    any_device.status = DeviceStatus.OFFLINE
    return any_device


@pytest.fixture
def any_ticket():
    return Ticket(client_id=str(hash("any_client_id")), service_number=str(hash("any_service_number")))
