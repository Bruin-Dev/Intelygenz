import asyncio

import aiohttp
import pytest
from aiohttp import ClientSession


@pytest.mark.integration
async def health_is_working_properly_test(client_session):
    response = await client_session.get("http://localhost:5000/_health")
    assert response.status == 200


@pytest.fixture
async def client_session():
    client_session = ClientSession()
    yield client_session
    await client_session.close()
