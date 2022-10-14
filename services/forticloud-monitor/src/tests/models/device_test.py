from application.models.device import DeviceStatus


def device_status_is_properly_checked_test(any_device):
    any_device.status = DeviceStatus.OFFLINE
    assert any_device.is_offline
