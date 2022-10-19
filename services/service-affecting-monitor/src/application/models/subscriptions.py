from dataclasses import dataclass

from framework.nats.models import Subscription
from framework.storage.task_dispatcher_client import TaskTypes

from config import config


@dataclass(kw_only=True)
class HandleTicketForward(Subscription):
    subject: str = f"task_dispatcher.{config.LOG_CONFIG['name']}.{TaskTypes.TICKET_FORWARDS.value}.success"
    queue: str = "task_dispatcher"
