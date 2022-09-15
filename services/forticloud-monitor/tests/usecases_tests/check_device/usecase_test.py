from unittest import mock
from unittest.mock import AsyncMock, Mock

import pytest
from conftest import CustomException
from usecases_tests.check_device.data import AnyDevice, AnyDeviceId, AnyTicket

from usecases.check_device import CheckDevice, DeviceRepository, DeviceStatus, TicketRepository

any_device_id = AnyDeviceId()
any_online_device = AnyDevice(status=DeviceStatus.ONLINE)
any_offline_device = AnyDevice(status=DeviceStatus.OFFLINE)


async def online_devices_have_no_ticket_stored_test(usecase_builder):
    # given
    store_ticket = AsyncMock()
    usecase = usecase_builder(
        get_device=AsyncMock(return_value=any_online_device),
        store_ticket=store_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    store_ticket.assert_not_awaited()


async def offline_devices_have_a_ticket_stored_test(usecase_builder):
    # given
    store_ticket = AsyncMock()
    usecase = usecase_builder(
        get_device=AsyncMock(return_value=any_offline_device),
        store_ticket=store_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    store_ticket.assert_awaited_once()


async def device_repository_errors_are_properly_propagated_test(usecase_builder):
    # given
    usecase = usecase_builder(get_device=AsyncMock(side_effect=CustomException))

    # then
    with pytest.raises(CustomException):
        await usecase(any_device_id)


async def ticket_building_errors_are_properly_propagated_test(usecase_builder):
    # given
    usecase = usecase_builder(
        get_device=AsyncMock(return_value=any_offline_device),
        build_ticket=Mock(side_effect=CustomException),
    )

    # then
    with pytest.raises(CustomException):
        await usecase(any_device_id)


async def ticket_repository_errors_are_properly_propagated_test(usecase_builder):
    # given
    usecase = usecase_builder(
        get_device=AsyncMock(return_value=any_offline_device),
        store_ticket=AsyncMock(side_effect=CustomException),
    )

    # then
    with pytest.raises(CustomException):
        await usecase(any_device_id)


@pytest.fixture
def usecase_builder(build_ticket_for):
    def builder(
        get_device: AsyncMock = AsyncMock(return_value=AnyDevice()),
        store_ticket: AsyncMock = AsyncMock(),
        build_ticket: Mock = Mock(return_value=AnyTicket()),
    ):
        build_ticket_for.return_value = build_ticket.return_value
        build_ticket_for.side_effect = build_ticket.side_effect

        device_repository = DeviceRepository()
        device_repository.get = get_device

        ticket_repository = TicketRepository(Mock(), Mock())
        ticket_repository.store = store_ticket

        return CheckDevice(device_repository, ticket_repository)

    return builder


@pytest.fixture
def build_ticket_for() -> Mock:
    with mock.patch("usecases.check_device.usecase.build_ticket_for") as build_ticket_for:
        yield build_ticket_for
