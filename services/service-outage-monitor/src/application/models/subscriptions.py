from config import config
from dataclasses import dataclass
from framework.nats.models import Subscription
from framework.storage.task_dispatcher_client import TaskTypes


@dataclass(kw_only=True)
class HandleTicketForwardSuccess(Subscription):
    subject: str = f"task_dispatcher.{config.LOG_CONFIG['name']}.{TaskTypes.TICKET_FORWARDS.value}.success"
    queue: str = "task_dispatcher"