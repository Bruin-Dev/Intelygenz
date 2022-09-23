import asyncio

import pytest


@pytest.mark.integration
async def some_test():
    await asyncio.sleep(1)
    assert True
