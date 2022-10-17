from unittest.mock import AsyncMock, Mock

import pytest

from application.domain.errors import AutoResolutionError
from application.domain.note import Note
from application.domain.task import TicketTask


async def online_devices_have_no_repair_ticket_posted_test(any_check_device, any_online_device, any_device_id):
    # given
    post_repair_ticket = AsyncMock()
    check_device = any_check_device(
        get_device=AsyncMock(return_value=any_online_device),
        post_repair_ticket=post_repair_ticket,
    )

    # when
    await check_device(any_device_id)

    # then
    post_repair_ticket.assert_not_awaited()


async def open_automation_tickets_are_properly_queried_test(any_check_online_device, any_device_id, any_ticket):
    # given
    find_open_automation_ticket_for = AsyncMock(return_value=any_ticket)
    check_device = any_check_online_device(find_open_automation_ticket_for=find_open_automation_ticket_for)

    # when
    await check_device(any_device_id)

    # then
    find_open_automation_ticket_for.assert_awaited_once_with(device_id=any_device_id)


async def ticketless_devices_arent_auto_resolved_test(any_check_online_device, any_device_id):
    # given
    resolve_task = AsyncMock()
    check_device = any_check_online_device(
        find_open_automation_ticket_for=AsyncMock(return_value=None),
        resolve_task=resolve_task,
    )

    # when
    await check_device(any_device_id)

    # then
    resolve_task.assert_not_awaited()


async def auto_resolution_errors_are_properly_handled_test(any_check_online_device, any_device_id, any_ticket):
    # given
    resolve_task = AsyncMock()
    any_ticket.auto_resolve = Mock(side_effect=AutoResolutionError)
    check_device = any_check_online_device(
        find_open_automation_ticket_for=AsyncMock(return_value=any_ticket),
        resolve_task=resolve_task,
    )

    # when
    await check_device(any_device_id)

    # then
    resolve_task.assert_not_awaited()


async def auto_resolved_tasks_are_properly_unpaused_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_task,
):
    # given
    unpause_task = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        found_ticket_id="any_ticket_id",
        found_ticket_task=any_task,
        unpause_task=unpause_task,
    )

    # when
    await check_device(any_device_id)

    # then
    unpause_task.assert_awaited_once_with(ticket_id="any_ticket_id", task=any_task)


async def auto_resolved_tasks_are_properly_handled_test(any_auto_resolved_task_scenario, any_device_id, any_task):
    # given
    resolve_task = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        found_ticket_id="any_ticket_id",
        found_ticket_task=any_task,
        resolve_task=resolve_task,
    )

    # when
    await check_device(any_device_id)

    # then
    resolve_task.assert_awaited_once_with(ticket_id="any_ticket_id", task=any_task)


async def tasks_that_could_not_be_unpaused_are_properly_resolved_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_exception,
):
    # given
    resolve_task = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        unpause_task=AsyncMock(side_effect=any_exception),
        resolve_task=resolve_task,
    )

    # when
    await check_device(any_device_id)

    # then
    resolve_task.assert_awaited_once()


async def auto_resolved_tasks_are_properly_monitored_test(any_auto_resolved_task_scenario, any_device_id):
    # given
    add_auto_resolved_task_metric = AsyncMock()
    check_device = any_auto_resolved_task_scenario(add_auto_resolved_task_metric=add_auto_resolved_task_metric)

    # when
    await check_device(any_device_id)

    # then
    add_auto_resolved_task_metric.assert_awaited_once()


async def only_properly_resolved_tasks_are_monitored_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_exception,
):
    # given
    add_auto_resolved_task_metric = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        resolve_task=AsyncMock(side_effect=any_exception),
        add_auto_resolved_task_metric=add_auto_resolved_task_metric,
    )

    # when
    await check_device(any_device_id)

    # then
    add_auto_resolved_task_metric.assert_not_awaited()


async def auto_resolved_tasks_have_a_proper_note_appended_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_task,
):
    # given
    post_ticket_note = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        found_ticket_id="any_ticket_id",
        found_ticket_task=any_task,
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_awaited_once_with(
        note=Note(
            ticket_id="any_ticket_id",
            service_number=any_task.service_number,
            text=any_task.auto_resolution_note_text,
        )
    )


async def only_properly_resolved_tasks_have_a_note_appended_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_exception,
):
    # given
    post_ticket_note = AsyncMock()
    check_device = any_auto_resolved_task_scenario(
        resolve_task=AsyncMock(side_effect=any_exception),
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_not_awaited()


async def errors_posting_auto_resolved_notes_wont_be_reraised_test(
    any_auto_resolved_task_scenario,
    any_device_id,
    any_exception,
):
    # given
    check_device = any_auto_resolved_task_scenario(post_ticket_note=AsyncMock(side_effect=any_exception))

    # then
    try:
        await check_device(any_device_id)
    except Exception:
        assert False


@pytest.fixture
def any_auto_resolved_task_scenario(any_check_device, any_online_device, any_ticket, any_task):
    def builder(
        found_ticket_id: str = "any_ticket_id",
        found_ticket_task: TicketTask = any_task,
        unpause_task: AsyncMock = AsyncMock(),
        resolve_task: AsyncMock = AsyncMock(),
        add_auto_resolved_task_metric: AsyncMock = AsyncMock(),
        post_ticket_note: AsyncMock = AsyncMock(),
    ):
        any_ticket.id = found_ticket_id
        any_ticket.auto_resolve = Mock(return_value=found_ticket_task)
        return any_check_device(
            get_device=AsyncMock(return_value=any_online_device),
            find_open_automation_ticket_for=AsyncMock(return_value=any_ticket),
            unpause_task=unpause_task,
            resolve_task=resolve_task,
            add_auto_resolved_task_metric=add_auto_resolved_task_metric,
            post_ticket_note=post_ticket_note,
        )

    return builder


@pytest.fixture
def any_check_online_device(any_check_device, any_online_device, any_ticket):
    def builder(
        find_open_automation_ticket_for: AsyncMock = AsyncMock(return_value=any_ticket),
        unpause_task: AsyncMock = AsyncMock(),
        resolve_task: AsyncMock = AsyncMock(),
        add_auto_resolved_task_metric: AsyncMock = AsyncMock(),
        post_ticket_note: AsyncMock = AsyncMock(),
    ):
        return any_check_device(
            get_device=AsyncMock(return_value=any_online_device),
            find_open_automation_ticket_for=find_open_automation_ticket_for,
            unpause_task=unpause_task,
            resolve_task=resolve_task,
            add_auto_resolved_task_metric=add_auto_resolved_task_metric,
            post_ticket_note=post_ticket_note,
        )

    return builder
