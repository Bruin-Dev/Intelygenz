from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional

from application.models.service_number import ServiceNumber


class TaskCycleStatus(Enum):
    ONGOING = auto()
    AUTO_RESOLVED = auto()


@dataclass
class TaskCycle:
    created_at: datetime
    status: TaskCycleStatus

    def started_in_the_last(self, duration: timedelta) -> bool:
        return self.created_at + duration >= datetime.utcnow()


class TaskStatus(Enum):
    ONGOING = auto()
    RESOLVED = auto()


@dataclass
class TicketTask:
    id: str
    service_number: ServiceNumber
    auto_resolution_grace_period: timedelta
    max_auto_resolutions: int
    status: TaskStatus
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
