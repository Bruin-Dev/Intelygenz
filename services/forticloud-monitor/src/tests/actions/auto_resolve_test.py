from unittest.mock import AsyncMock

import pytest

from application.actions import CheckDevice
from application.models.task import TicketTask


@pytest.mark.skip
async def online_devices_properly_auto_resolve_tickets_test(any_online_device, any_ticket):
    # given
    ticket = Ticket(created_by="", details=[TicketTask(service_number=any_online_device.id.service_number)], notes=[])
    check_device = any_check_device(
        get_device=AsyncMock(return_value=any_online_device),
    )

    # when


@pytest.fixture
def any_check_device(any_offline_device, any_created_ticket):
    def builder(
        get_device: AsyncMock = AsyncMock(return_value=any_offline_device),
        post_repair_ticket: AsyncMock = AsyncMock(return_value=any_created_ticket),
        post_ticket_note: AsyncMock = AsyncMock(),
    ) -> CheckDevice:
        forticloud_repository = Mock(ForticloudRepository)
        forticloud_repository.get_device = get_device

        bruin_repository = Mock(BruinRepository)
        bruin_repository.post_repair_ticket = post_repair_ticket
        bruin_repository.post_ticket_note = post_ticket_note

        return CheckDevice(forticloud_repository, bruin_repository)

    return builder


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
