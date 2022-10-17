from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pytest

from application.domain.task import ServiceNumber, TaskCycle, TaskCycleStatus, TaskStatus, TicketTask
from application.domain.ticket import (
    AutoResolutionGracePeriodExpiredError,
    MaxTaskAutoResolutionsReachedError,
    ServiceNumberHasNoTaskError,
    ServiceNumberTaskWasAlreadyResolvedError,
    Ticket,
)


def any_ticket(
    id: str = "any_id",
    created_at: datetime = datetime.utcnow(),
    tasks: Optional[Dict[ServiceNumber, TicketTask]] = None,
):
    return Ticket(id=id, created_at=created_at, tasks=tasks or {})


def any_ticket_task(
    id: str = "any_id",
    service_number: ServiceNumber = "any_service_number",
    auto_resolution_grace_period: timedelta = timedelta(minutes=90),
    max_auto_resolutions: int = 3,
    status: TaskStatus = TaskStatus.ONGOING,
    cycles: Optional[List[TaskCycle]] = None,
):
    return TicketTask(
        id=id,
        service_number=service_number,
        auto_resolution_grace_period=auto_resolution_grace_period,
        max_auto_resolutions=max_auto_resolutions,
        status=status,
        cycles=cycles or [],
    )


def any_cycle(
    created_at: datetime = datetime.utcnow(),
    status: TaskCycleStatus = TaskCycleStatus.ONGOING,
):
    return TaskCycle(created_at=created_at, status=status)


@pytest.mark.parametrize(
    "ticket_tasks",
    [
        ({}),
        ({"any_service_number": any_ticket_task()}),
        ({"any_service_number": any_ticket_task(), "any_other_service_number": any_ticket_task()}),
    ],
    ids=["empty_tasks", "any_single_task", "any_multiple_tasks"],
)
def unexisting_service_number_tasks_cannot_be_auto_resolved_test(ticket_tasks):
    # given
    ticket = any_ticket(tasks=ticket_tasks)

    # then
    with pytest.raises(ServiceNumberHasNoTaskError):
        ticket.auto_resolve(ServiceNumber("any_unexisting_service_number"))


def resolved_tasks_cannot_be_auto_resolved_test():
    # given
    service_number = ServiceNumber("any_service_number")
    ticket = any_ticket(
        tasks={
            service_number: any_ticket_task(status=TaskStatus.RESOLVED),
        }
    )

    # then
    with pytest.raises(ServiceNumberTaskWasAlreadyResolvedError):
        ticket.auto_resolve(service_number)


@pytest.mark.parametrize(
    ["max_task_auto_resolutions", "task_cycles"],
    [
        (1, [any_cycle(status=TaskCycleStatus.AUTO_RESOLVED)]),
        (1, [any_cycle(status=TaskCycleStatus.AUTO_RESOLVED), any_cycle(status=TaskCycleStatus.AUTO_RESOLVED)]),
        (2, [any_cycle(status=TaskCycleStatus.AUTO_RESOLVED), any_cycle(status=TaskCycleStatus.AUTO_RESOLVED)]),
    ],
    ids=["max_one_auto_resolve_reached", "max_two_auto_resolves_reached", "max_one_auto_resolve_exceeded"],
)
def tasks_can_only_be_auto_resolved_a_number_of_times_test(max_task_auto_resolutions, task_cycles):
    service_number = ServiceNumber("any_service_number")
    ticket = any_ticket(
        tasks={
            service_number: any_ticket_task(
                service_number=service_number,
                max_auto_resolutions=max_task_auto_resolutions,
                cycles=task_cycles,
            ),
        },
    )

    # then
    with pytest.raises(MaxTaskAutoResolutionsReachedError):
        ticket.auto_resolve(service_number)


@pytest.mark.parametrize(
    ["auto_resolution_grace_period", "task_cycles"],
    [
        (
            timedelta(seconds=5),
            [
                any_cycle(
                    status=TaskCycleStatus.ONGOING,
                    created_at=datetime.utcnow() - timedelta(seconds=10),
                )
            ],
        ),
        (
            timedelta(seconds=5),
            [
                any_cycle(
                    status=TaskCycleStatus.AUTO_RESOLVED,
                    created_at=datetime.utcnow() - timedelta(seconds=20),
                ),
                any_cycle(
                    status=TaskCycleStatus.ONGOING,
                    created_at=datetime.utcnow() - timedelta(seconds=10),
                ),
            ],
        ),
        (
            timedelta(seconds=5),
            [
                any_cycle(
                    status=TaskCycleStatus.ONGOING,
                    created_at=datetime.utcnow() - timedelta(seconds=10),
                ),
                any_cycle(
                    status=TaskCycleStatus.AUTO_RESOLVED,
                    created_at=datetime.utcnow() - timedelta(seconds=20),
                ),
            ],
        ),
    ],
    ids=[
        "ongoing_cycle_created_too_long_ago",
        "new_ongoing_cycle_created_too_long_ago",
        "new_ongoing_cycle_in_unsorted_cycles_created_too_long_ago",
    ],
)
def auto_resolution_grace_period_expired_tasks_cannot_be_auto_resolved_test(auto_resolution_grace_period, task_cycles):
    # given
    service_number = ServiceNumber("any_service_number")
    ticket = any_ticket(
        tasks={
            service_number: any_ticket_task(
                service_number=service_number,
                auto_resolution_grace_period=auto_resolution_grace_period,
                cycles=task_cycles,
            ),
        },
    )

    # then
    with pytest.raises(AutoResolutionGracePeriodExpiredError):
        ticket.auto_resolve(service_number)


@pytest.mark.parametrize(
    ["auto_resolution_grace_period", "task_cycles"],
    [
        (
            timedelta(seconds=15),
            [
                any_cycle(
                    status=TaskCycleStatus.ONGOING,
                    created_at=datetime.utcnow() - timedelta(seconds=10),
                )
            ],
        ),
        (
            timedelta(seconds=15),
            [
                any_cycle(
                    status=TaskCycleStatus.AUTO_RESOLVED,
                    created_at=datetime.utcnow() - timedelta(seconds=10),
                ),
                any_cycle(
                    status=TaskCycleStatus.ONGOING,
                    created_at=datetime.utcnow() - timedelta(seconds=5),
                ),
            ],
        ),
    ],
    ids=["triage_note_recently_added", "reopen_note_recently_added"],
)
def recent_tasks_can_be_auto_resolved_test(auto_resolution_grace_period, task_cycles):
    # given
    service_number = ServiceNumber("any_service_number")
    task = any_ticket_task(
        id="any_task_id",
        service_number=service_number,
        auto_resolution_grace_period=auto_resolution_grace_period,
        cycles=task_cycles,
    )
    ticket = any_ticket(tasks={service_number: task})

    # when
    auto_resolved_task = ticket.auto_resolve(service_number)

    # then
    assert auto_resolved_task.status == TaskStatus.RESOLVED


#
# CORNER CASES
#


@pytest.mark.parametrize(
    ["ticket_created_at", "auto_resolution_grace_period", "task_cycles"],
    [
        # This can happen if we fail starting the cycle in Bruin when automatically creating a Ticket
        (
            datetime.utcnow() - timedelta(seconds=5),
            timedelta(seconds=10),
            [],
        ),
        # This can happen if a user manually starts a Resolved task
        (
            datetime.utcnow() - timedelta(seconds=20),
            timedelta(seconds=10),
            [any_cycle(status=TaskCycleStatus.AUTO_RESOLVED, created_at=datetime.utcnow() - timedelta(seconds=5))],
        ),
    ],
    ids=["no_cycles_task", "some_auto_resolved_cycles_task"],
)
def corner_case_task_cycles_are_properly_auto_resolved_test(
    ticket_created_at,
    auto_resolution_grace_period,
    task_cycles,
):
    # given
    service_number = ServiceNumber("any_service_number")
    task = any_ticket_task(
        status=TaskStatus.ONGOING,
        auto_resolution_grace_period=auto_resolution_grace_period,
        cycles=task_cycles,
    )
    ticket = any_ticket(created_at=ticket_created_at, tasks={service_number: task})

    # when
    auto_resolved_task = ticket.auto_resolve(service_number)

    # then
    assert auto_resolved_task.status == TaskStatus.RESOLVED


@pytest.mark.parametrize(
    ["ticket_created_at", "auto_resolution_grace_period", "task_cycles"],
    [
        # This can happen if we fail starting the cycle in Bruin when automatically creating a Ticket
        (
            datetime.utcnow() - timedelta(seconds=10),
            timedelta(seconds=5),
            [],
        ),
        # This can happen if a user manually starts a Resolved task
        (
            datetime.utcnow() - timedelta(seconds=20),
            timedelta(seconds=5),
            [any_cycle(status=TaskCycleStatus.AUTO_RESOLVED, created_at=datetime.utcnow() - timedelta(seconds=10))],
        ),
    ],
    ids=["no_cycles_task", "some_auto_resolved_cycles_task"],
)
def corner_case_task_cycles_raise_a_proper_exception_test(ticket_created_at, auto_resolution_grace_period, task_cycles):
    # given
    service_number = ServiceNumber("any_service_number")
    task = any_ticket_task(
        status=TaskStatus.ONGOING,
        auto_resolution_grace_period=auto_resolution_grace_period,
        cycles=task_cycles,
    )
    ticket = any_ticket(created_at=ticket_created_at, tasks={service_number: task})

    # then
    with pytest.raises(AutoResolutionGracePeriodExpiredError):
        ticket.auto_resolve(service_number)
