import igz
import pytest
from asynctest import CoroutineMock
from hypercorn.config import Config as HyperCornConfig
from igz.config import testconfig as config
from igz.packages.server.api import QuartServer
from quart import Quart, jsonify


class Testapi:
    def instantiation_test(self):
        testquarts = QuartServer(config)
        assert testquarts._title == config.QUART_CONFIG["title"]
        assert testquarts._port == config.QUART_CONFIG["port"]
        assert isinstance(testquarts._hypercorn_config, HyperCornConfig) is True
        assert testquarts._new_bind == f"0.0.0.0:{testquarts._port}"
        assert isinstance(testquarts._quart_server, Quart) is True
        assert testquarts._quart_server.title == testquarts._title

    def set_status_test(self):
        testquarts = QuartServer(config)
        testquarts.set_status(200)
        assert testquarts._status == 200

    @pytest.mark.asyncio
    async def run_server_test(self):
        testquarts = QuartServer(config)
        mock_serve = igz.packages.server.api.serve = CoroutineMock()
        await testquarts.run_server()
        assert testquarts._hypercorn_config.bind == [testquarts._new_bind]
        assert mock_serve.called

    @pytest.mark.asyncio
    async def ok_app_test(self):
        testquarts = QuartServer(config)
        client = testquarts._quart_server.test_client()
        response = await client.get("/_health")
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None
