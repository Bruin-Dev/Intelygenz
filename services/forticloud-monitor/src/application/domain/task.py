from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional

from application.domain.errors import (
    AutoResolutionGracePeriodExpiredError,
    MaxTaskAutoResolutionsReachedError,
    ServiceNumberTaskWasAlreadyResolvedError,
)
from application.domain.service_number import ServiceNumber

TRIAGE_HEADER = ["#*MetTel's IPA*#", "Forticloud triage.", ""]
REOPEN_HEADER = ["#*MetTel's IPA*#", "Re-opening ticket.", ""]
AUTO_RESOLUTION_HEADER = ["#*MetTel's IPA*#", "Auto-resolving task.", ""]
DEVICE_UP_EVENT = "Event: Device Up"
DEVICE_DOWN_EVENT = "Event: Device Down"


class TaskCycleStatus(Enum):
    ONGOING = auto()
    AUTO_RESOLVED = auto()


@dataclass
class TaskCycle:
    created_at: datetime
    status: TaskCycleStatus

    def started_in_the_last(self, duration: timedelta) -> bool:
        return self.created_at + duration >= datetime.utcnow()


@dataclass
class TicketTask:
    id: str
    service_number: ServiceNumber
    auto_resolution_grace_period: timedelta
    max_auto_resolutions: int
    is_resolved: bool
    cycles: List[TaskCycle] = field(default_factory=list)

    @property
    def last_cycle(self) -> Optional[TaskCycle]:
        if len(self.cycles) == 0:
            return None

        sorted_cycles = sorted(self.cycles, key=lambda n: n.created_at, reverse=True)
        return sorted_cycles[0]

    @property
    def times_auto_resolved(self):
        return len([cycle for cycle in self.cycles if cycle.status == TaskCycleStatus.AUTO_RESOLVED])

    def auto_resolve(self, ticket_creation_date: datetime):
        if self.is_resolved:
            raise ServiceNumberTaskWasAlreadyResolvedError()
        elif self.times_auto_resolved >= self.max_auto_resolutions:
            raise MaxTaskAutoResolutionsReachedError()

        last_cycle = self.last_cycle
        # If the task has no cycles, check the ticket date for auto resolution
        ticket_started_in_grace_period = ticket_creation_date + self.auto_resolution_grace_period >= datetime.utcnow()
        if not last_cycle and not ticket_started_in_grace_period:
            raise AutoResolutionGracePeriodExpiredError()
        # else, check the last cycle date for auto resolution
        elif last_cycle and not last_cycle.started_in_the_last(self.auto_resolution_grace_period):
            raise AutoResolutionGracePeriodExpiredError()

        self.is_resolved = True
        if last_cycle:
            last_cycle.status = TaskCycleStatus.AUTO_RESOLVED

    @property
    def auto_resolution_note_text(self) -> str:
        raise NotImplementedError
