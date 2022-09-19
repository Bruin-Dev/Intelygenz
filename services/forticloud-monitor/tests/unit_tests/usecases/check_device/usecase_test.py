from unittest.mock import AsyncMock, Mock

import pytest

from usecases.check_device import CheckDevice


async def online_devices_have_no_ticket_stored_test(scenario, any_online_device, any_device_id):
    # given
    store_ticket = AsyncMock()
    usecase = scenario(
        get_device=AsyncMock(return_value=any_online_device),
        store_ticket=store_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    store_ticket.assert_not_awaited()


async def offline_devices_have_a_ticket_stored_test(scenario, any_offline_device, any_device_id):
    # given
    store_ticket = AsyncMock()
    usecase = scenario(
        get_device=AsyncMock(return_value=any_offline_device),
        store_ticket=store_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    store_ticket.assert_awaited_once()


async def device_repository_errors_are_properly_propagated_test(scenario, any_device_id, any_exception):
    # given
    usecase = scenario(get_device=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await usecase(any_device_id)


async def ticket_building_errors_are_properly_propagated_test(
    scenario,
    any_offline_device,
    any_device_id,
    any_exception,
):
    # given
    usecase = scenario(
        get_device=AsyncMock(return_value=any_offline_device),
        build_ticket=Mock(side_effect=any_exception),
    )

    # then
    with pytest.raises(any_exception):
        await usecase(any_device_id)


async def ticket_repository_errors_are_properly_propagated_test(
    scenario,
    any_offline_device,
    any_device_id,
    any_exception,
):
    # given
    usecase = scenario(
        get_device=AsyncMock(return_value=any_offline_device),
        store_ticket=AsyncMock(side_effect=any_exception),
    )

    # then
    with pytest.raises(any_exception):
        await usecase(any_device_id)


@pytest.fixture
def scenario(any_device, any_ticket):
    def builder(
        get_device: AsyncMock = AsyncMock(return_value=any_device),
        store_ticket: AsyncMock = AsyncMock(),
        build_ticket: Mock = Mock(return_value=any_ticket),
    ):
        return CheckDevice(get_device=get_device, store_ticket=store_ticket, build_ticket=build_ticket)

    return builder
