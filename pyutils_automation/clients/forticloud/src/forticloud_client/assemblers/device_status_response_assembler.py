def device_status_response_assembler(device_response):
    device_status_assembled = {"status": device_response["status"], "body": None}
    if device_response["body"]:
        device_status_assembled["body"] = {"status_device": device_response["body"]["status"]}
    return device_status_assembled
