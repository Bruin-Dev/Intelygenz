from unittest.mock import AsyncMock, Mock

import pytest
from check_device_tests.data import AnyDevice, AnyDeviceId, AnyTicket

from check_device.device import DeviceStatus
from check_device.device_repository import DeviceRepository
from check_device.ticket_repository import TicketRepository
from check_device.ticket_service import TicketService
from check_device.usecase import CheckDevice


async def test_an_online_device_stores_no_ticket(
    device_repository: DeviceRepository,
    ticket_repository: TicketRepository,
):
    # given
    an_online_device = AnyDevice(status=DeviceStatus.ONLINE)
    device_repository.get = AsyncMock(return_value=an_online_device)
    ticket_repository.store = AsyncMock()

    # when
    check_device = CheckDevice(device_repository, ticket_repository, Mock(TicketService))
    await check_device(AnyDeviceId())

    # then
    ticket_repository.store.assert_not_awaited()


async def test_an_offline_device_stores_a_ticket(
    device_repository: DeviceRepository,
    ticket_repository: TicketRepository,
    ticket_service: TicketService,
):
    # given
    an_offline_device = AnyDevice(status=DeviceStatus.OFFLINE)
    a_ticket = AnyTicket()

    device_repository.find = AsyncMock(return_value=an_offline_device)
    ticket_repository.store = AsyncMock()
    ticket_service.build_ticket_for = Mock(return_value=a_ticket)

    # when
    check_device = CheckDevice(device_repository, ticket_repository, ticket_service)
    await check_device(AnyDeviceId())

    # then
    ticket_repository.store.assert_awaited_once_with(a_ticket)


@pytest.fixture
def device_repository() -> DeviceRepository:
    return Mock(DeviceRepository)


@pytest.fixture
def ticket_repository() -> TicketRepository:
    return Mock(TicketRepository)


@pytest.fixture
def ticket_service() -> TicketService:
    return Mock(TicketService)
