import json
import logging

from nats.aio.msg import Msg

from application import ForwardQueues

logger = logging.getLogger(__name__)


class HandleTicketForward:
    def __init__(self, metrics_repository, bruin_repository):
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository

    async def success(self, msg: Msg):
        payload = json.loads(msg.data)
        ticket_id = payload["ticket_id"]
        serial_number = payload["serial_number"]
        target_queue = payload["target_queue"]

        logger.info(f"Successfully forwarded ticket {ticket_id} and serial {serial_number} to {target_queue}")
        self._metrics_repository.increment_tasks_forwarded(**payload["metrics_labels"])

        if target_queue == ForwardQueues.HNOC.value:
            await self._bruin_repository.send_forward_email_milestone_notification(ticket_id, serial_number)
