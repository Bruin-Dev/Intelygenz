from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Dict

from application.models.service_number import ServiceNumber
from application.models.task import TaskCycleStatus, TaskStatus, TicketTask


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

    def auto_resolve_task_for(self, service_number: ServiceNumber) -> TicketTask:
        task = self.tasks.get(service_number)

        if not task:
            raise ServiceNumberHasNoTaskError()
        elif task.status == TaskStatus.RESOLVED:
            raise ServiceNumberTaskWasAlreadyResolvedError()
        elif task.max_auto_resolutions <= task.times_auto_resolved:
            raise MaxTaskAutoResolutionsReachedError()

        last_cycle = task.last_cycle
        # If the task has no cycles, check the ticket date for auto resolution
        if not last_cycle and not self.started_in_the_last(task.auto_resolution_grace_period):
            raise AutoResolutionGracePeriodExpiredError()
        # else, check the last cycle date for auto resolution
        elif last_cycle and not last_cycle.started_in_the_last(task.auto_resolution_grace_period):
            raise AutoResolutionGracePeriodExpiredError()

        task.status = TaskStatus.RESOLVED
        if last_cycle:
            last_cycle.status = TaskCycleStatus.AUTO_RESOLVED

        return task

    def started_in_the_last(self, duration: timedelta) -> bool:
        return self.created_at + duration >= datetime.utcnow()


class AutoResolutionGracePeriodExpiredError(Exception):
    pass


class MaxTaskAutoResolutionsReachedError(Exception):
    pass


class ServiceNumberHasNoTaskError(Exception):
    pass


class ServiceNumberTaskWasAlreadyResolvedError(Exception):
    pass
