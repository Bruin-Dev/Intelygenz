from forticloud_client.assemblers.device_status_response_assembler import device_status_response_assembler

RESPONSE_DEVICE = {"status": 200, "body": {"status": "offline"}}
RESPONSE_DEVICE_WITHOUT_BODY = {"status": 200, "body": []}


def device_status_response_assembler_return_not_none_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE)
    assert device_status_response_assembled is not None


def device_status_response_assembler_return_status_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE)
    assert "status" in device_status_response_assembled


def device_status_response_assembler_return_same_status_than_strategy_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE)
    assert device_status_response_assembled["status"] == RESPONSE_DEVICE["status"]


def device_status_response_assembler_return_body_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE)
    assert "body" in device_status_response_assembled


def device_status_response_assembler_return_none_if_not_body_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE_WITHOUT_BODY)
    assert device_status_response_assembled["body"] is None


def device_status_response_assembler_return_status_device_in_body_test():
    device_status_response_assembled = device_status_response_assembler(RESPONSE_DEVICE)
    assert "status_device" in device_status_response_assembled["body"]
