from typing import Callable
from unittest.mock import AsyncMock, Mock

import pytest
from check_device_test.fixtures import (
    AnyDevice,
    AnyDeviceId,
    AnyOfflineDevice,
    AnyOnlineDevice,
    AnyTicket,
    CustomException,
)

from check_device.device import Device, DeviceStatus
from check_device.device_repository import DeviceRepository
from check_device.ticket import Ticket
from check_device.ticket_repository import TicketRepository
from check_device.ticket_service import TicketService
from check_device.usecase import CheckDevice


async def checked_online_devices_have_no_ticket_stored_test(setup_usecase):
    # given
    check_device = setup_usecase(found_device=AnyOnlineDevice())
    check_device.ticket_repository.store = AsyncMock()

    # when
    await check_device(AnyDeviceId())

    # then
    check_device.ticket_repository.store.assert_not_awaited()


async def checked_offline_devices_have_a_ticket_stored_test(setup_usecase):
    # given
    a_ticket = AnyTicket()
    check_device = setup_usecase(found_device=AnyOfflineDevice(), generated_ticket=a_ticket)
    check_device.ticket_repository.store = AsyncMock()

    # when
    await check_device(AnyDeviceId())

    # then
    check_device.ticket_repository.store.assert_awaited_once_with(a_ticket)


async def device_repository_errors_are_properly_propagated_test(setup_usecase):
    # given
    check_device = setup_usecase()
    check_device.device_repository.get = AsyncMock(side_effect=CustomException)

    # then
    with pytest.raises(CustomException):
        await check_device(AnyDeviceId())


async def ticket_service_errors_are_properly_propagated_test(setup_usecase):
    # given
    check_device = setup_usecase(found_device=AnyOfflineDevice())
    check_device.ticket_service.build_ticket_for = Mock(side_effect=CustomException)

    # then
    with pytest.raises(CustomException):
        await check_device(AnyDeviceId())


async def ticket_repository_errors_are_properly_propagated_test(setup_usecase):
    # given
    check_device = setup_usecase(found_device=AnyOfflineDevice())
    check_device.ticket_repository.store = AsyncMock(side_effect=CustomException)

    # then
    with pytest.raises(CustomException):
        await check_device(AnyDeviceId())


@pytest.fixture
def check_device() -> CheckDevice:
    return CheckDevice(Mock(DeviceRepository), Mock(TicketRepository), Mock(TicketService))


@pytest.fixture
def setup_usecase() -> Callable[..., CheckDevice]:
    def builder(
        found_device: Device = AnyDevice(status=DeviceStatus.ONLINE),
        generated_ticket: Ticket = AnyTicket(),
    ):
        check_device = CheckDevice(Mock(DeviceRepository), Mock(TicketRepository), Mock(TicketService))
        check_device.device_repository.get = AsyncMock(return_value=found_device)
        check_device.ticket_service.build_ticket_for = Mock(return_value=generated_ticket)
        return check_device

    return builder
