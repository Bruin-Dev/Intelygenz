from unittest.mock import AsyncMock, Mock, patch

import pytest

from application.actions.check_device import CheckDevice
from application.domain.device import Device
from application.domain.note import Note
from application.domain.ticket import CreatedTicket, TicketStatus


async def offline_devices_have_a_repair_ticket_posted_test(any_check_device, any_offline_device, any_device_id):
    # given
    post_repair_ticket = AsyncMock()
    check_device = any_check_device(
        get_device=AsyncMock(return_value=any_offline_device),
        post_repair_ticket=post_repair_ticket,
    )

    # when
    await check_device(any_device_id)

    # then
    post_repair_ticket.assert_awaited_once()


@patch("application.actions.check_device.build_note")
async def created_tickets_note_texts_are_properly_built_test(
    build_note: Mock,
    any_check_offline_device,
    any_offline_device,
    any_device_id,
):
    # given
    check_device = any_check_offline_device(
        device=any_offline_device,
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.CREATED),
    )

    # when
    await check_device(any_device_id)

    # then
    build_note.assert_called_once_with(any_offline_device)


@patch("application.actions.check_device.build_note")
async def created_tickets_have_a_proper_note_appended_test(build_note: Mock, any_check_offline_device, any_device_id):
    # given
    build_note.return_value = "any_note"
    post_ticket_note = AsyncMock()
    check_device = any_check_offline_device(
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.CREATED),
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_awaited_once_with(
        Note(
            ticket_id="any_ticket_id",
            service_number=any_device_id.service_number,
            text="any_note",
        )
    )


async def in_progress_tickets_have_no_note_appended_test(any_check_offline_device, any_device_id):
    # given
    post_ticket_note = AsyncMock()
    check_device = any_check_offline_device(
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.IN_PROGRESS),
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_not_awaited()


async def failed_reopening_tickets_raise_a_proper_exception_test(any_check_offline_device, any_device_id):
    # given
    check_device = any_check_offline_device(
        created_ticket=CreatedTicket(
            ticket_id="any_ticket_id",
            ticket_status=TicketStatus.FAILED_REOPENING,
        )
    )

    # then
    with pytest.raises(Exception):
        await check_device(any_device_id)


@patch("application.actions.check_device.build_note")
async def reopened_ticket_note_texts_are_properly_built_test(
    build_note: Mock,
    any_check_offline_device,
    any_offline_device,
    any_device_id,
):
    # given
    check_device = any_check_offline_device(
        device=any_offline_device,
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.REOPENED),
    )

    # when
    await check_device(any_device_id)

    # then
    build_note.assert_called_once_with(any_offline_device, is_reopen_note=True)


@patch("application.actions.check_device.build_note")
async def reopened_tickets_have_a_proper_note_appended_test(
    build_note: Mock,
    any_check_offline_device,
    any_device_id,
):
    # given
    build_note.return_value = "any_note"
    post_ticket_note = AsyncMock()
    check_device = any_check_offline_device(
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.REOPENED),
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_awaited_once_with(
        Note(
            ticket_id="any_ticket_id",
            service_number=any_device_id.service_number,
            text="any_note",
        )
    )


@patch("application.actions.check_device.build_note")
async def reopened_same_location_ticket_note_texts_are_properly_built_test(
    build_note: Mock,
    any_check_offline_device,
    any_offline_device,
    any_device_id,
):
    # given
    check_device = any_check_offline_device(
        device=any_offline_device,
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.REOPENED_SAME_LOCATION),
    )

    # when
    await check_device(any_device_id)

    # then
    build_note.assert_called_once_with(any_offline_device)


@patch("application.actions.check_device.build_note")
async def reopened_same_location_tickets_have_a_proper_note_appended_test(
    build_note: Mock,
    any_check_offline_device,
    any_device_id,
):
    # given
    build_note.return_value = "any_note"
    post_ticket_note = AsyncMock()
    check_device = any_check_offline_device(
        created_ticket=CreatedTicket(ticket_id="any_ticket_id", ticket_status=TicketStatus.REOPENED_SAME_LOCATION),
        post_ticket_note=post_ticket_note,
    )

    # when
    await check_device(any_device_id)

    # then
    post_ticket_note.assert_awaited_once_with(
        Note(
            ticket_id="any_ticket_id",
            service_number=any_device_id.service_number,
            text="any_note",
        )
    )


async def post_repair_ticket_errors_are_properly_propagated_test(
    any_check_device,
    any_offline_device,
    any_device_id,
    any_exception,
):
    # given
    check_device = any_check_device(
        get_device=AsyncMock(return_value=any_offline_device),
        post_repair_ticket=AsyncMock(side_effect=any_exception),
    )

    # then
    with pytest.raises(any_exception):
        await check_device(any_device_id)


@pytest.fixture
def any_check_offline_device(any_offline_device, any_check_device):
    def builder(
        created_ticket: CreatedTicket,
        device: Device = any_offline_device,
        post_ticket_note: AsyncMock = AsyncMock(),
    ) -> CheckDevice:
        return any_check_device(
            get_device=AsyncMock(return_value=device),
            post_repair_ticket=AsyncMock(return_value=created_ticket),
            post_ticket_note=post_ticket_note,
        )

    return builder
