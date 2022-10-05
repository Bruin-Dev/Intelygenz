from application.repositories.assemblers.device_assembler import build_device_with_client_id

DEVICE = {"serial_number": "sn1"}
CLIENT_ID = 1234


def build_device_with_client_id_return_not_none_test():
    device_with_client_id = build_device_with_client_id(device=DEVICE, client_id=CLIENT_ID)
    assert device_with_client_id is not None


def build_device_with_client_id_return_none_where_not_client_id_test():
    device_with_client_id = build_device_with_client_id(device=DEVICE, client_id=None)
    assert device_with_client_id is None


def build_device_with_client_id_return_device_with_client_id_test():
    device_with_client_id = build_device_with_client_id(device=DEVICE, client_id=CLIENT_ID)
    assert "client_id" in device_with_client_id
