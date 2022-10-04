def device_status_is_properly_checked_test(any_offline_device):
    assert any_offline_device.is_offline
