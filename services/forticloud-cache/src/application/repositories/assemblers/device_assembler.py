import logging

logger = logging.getLogger(__name__)


def build_device_with_client_id(device, client_id):
    if not client_id:
        logger.warning(f"Can't find client id for device: {device}")
        device = None
    else:
        device["client_id"] = client_id
    return device
