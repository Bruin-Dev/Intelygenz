from unittest.mock import AsyncMock

import pytest


async def get_device_errors_are_properly_propagated_test(any_check_device, any_device_id, any_exception):
    # given
    check_device = any_check_device(get_device=AsyncMock(side_effect=any_exception))

    # then
    with pytest.raises(any_exception):
        await check_device(any_device_id)
