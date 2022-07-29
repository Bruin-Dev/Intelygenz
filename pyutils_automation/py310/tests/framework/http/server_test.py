from unittest.mock import AsyncMock, patch

import framework
from framework.http.server import Config as QuartConfig
from framework.http.server import Server as QuartServer
from pytest import fixture


@fixture(scope="module")
def quart_server():
    cfg = QuartConfig(port="any_port")
    return QuartServer(cfg)


async def run_server_test(quart_server):
    # Given
    client = quart_server.server.test_client()

    # When
    with patch.object(framework.http.server, "serve", new=AsyncMock()):
        await quart_server.run()
        response = await client.get("/")

    # Then
    assert response.status_code is not None


async def health_endpoint_test(quart_server):
    # Given
    client = quart_server.server.test_client()

    # When
    response = await client.get("/_health")

    # Then
    assert response.status_code == 200
