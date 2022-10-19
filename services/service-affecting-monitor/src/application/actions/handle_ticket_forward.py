import json
import logging

from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class HandleTicketForward:
    def __init__(self, metrics_repository):
        self._metrics_repository = metrics_repository

    async def success(self, msg: Msg):
        payload = json.loads(msg.data)

        ticket_id = payload["ticket_id"]
        serial_number = payload["serial_number"]
        target_queue = payload["target_queue"]

        logger.info(f"Successfully forwarded ticket {ticket_id} and serial {serial_number} to {target_queue}")
        self._metrics_repository.increment_tasks_forwarded(**payload["metrics_labels"])
