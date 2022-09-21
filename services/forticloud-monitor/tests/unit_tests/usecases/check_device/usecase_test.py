from unittest.mock import AsyncMock

import pytest

from usecases.check_device import CheckDevice


async def online_devices_have_no_ticket_created_test(scenario, any_online_device, any_device_id):
    # given
    create_ticket = AsyncMock()
    usecase = scenario(
        get_device=AsyncMock(return_value=any_online_device),
        create_ticket=create_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    create_ticket.assert_not_awaited()


async def offline_devices_have_a_ticket_created_test(scenario, any_offline_device, any_device_id):
    # given
    create_ticket = AsyncMock()
    usecase = scenario(
        get_device=AsyncMock(return_value=any_offline_device),
        create_ticket=create_ticket,
    )

    # when
    await usecase(any_device_id)

    # then
    create_ticket.assert_awaited_once()


async def get_device_errors_are_properly_propagated_test(scenario, any_device_id, any_exception):
    # given
    usecase = scenario(get_device=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await usecase(any_device_id)


async def create_ticket_errors_are_properly_propagated_test(
    scenario,
    any_offline_device,
    any_device_id,
    any_exception,
):
    # given
    usecase = scenario(
        get_device=AsyncMock(return_value=any_offline_device),
        create_ticket=AsyncMock(side_effect=any_exception),
    )

    # then
    with pytest.raises(any_exception):
        await usecase(any_device_id)


@pytest.fixture
def scenario(any_device, any_created_ticket):
    def builder(
        get_device: AsyncMock = AsyncMock(return_value=any_device),
        create_ticket: AsyncMock = AsyncMock(return_value=any_created_ticket),
    ):
        return CheckDevice(get_device=get_device, create_ticket=create_ticket)

    return builder
