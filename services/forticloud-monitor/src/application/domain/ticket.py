from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Dict

from application.domain.errors import ServiceNumberHasNoTaskError
from application.domain.service_number import ServiceNumber
from application.domain.task import TicketTask


class TicketStatus(IntEnum):
    CREATED = 200
    IN_PROGRESS = 409
    FAILED_REOPENING = 471
    REOPENED = 472
    REOPENED_SAME_LOCATION = 473


@dataclass
class CreatedTicket:
    ticket_id: str
    ticket_status: TicketStatus


@dataclass
class Ticket:
    id: str
    created_at: datetime
    tasks: Dict[ServiceNumber, TicketTask] = field(default_factory=dict)

    def auto_resolve(self, service_number: ServiceNumber) -> TicketTask:
        task = self.tasks.get(service_number)

        if not task:
            raise ServiceNumberHasNoTaskError()

        task.auto_resolve(ticket_creation_date=self.created_at)
        return task
