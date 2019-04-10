import igz
from igz.packages.server.api import QuartServer
import pytest
from igz.config import testconfig as config
from quart_openapi import Pint
from hypercorn.config import Config as HyperCornConfig
from asynctest import CoroutineMock


class Testapi:

    def instantiation_test(self):
        testquarts = QuartServer(config)
        assert testquarts._title == config.QUART_CONFIG['title']
        assert testquarts._port == config.QUART_CONFIG['port']
        assert isinstance(testquarts._corn_config, HyperCornConfig) is True
        assert testquarts._new_bind == f'0.0.0.0:{testquarts._port}'
        assert isinstance(testquarts._quart_server, Pint) is True
        assert testquarts._quart_server.title == testquarts._title

    @pytest.mark.asyncio
    async def run_server_test(self):
        testquarts = QuartServer(config)
        mock_serve = igz.packages.server.api.serve = CoroutineMock()
        await testquarts.run_server()
        assert testquarts._corn_config.bind == [testquarts._new_bind]
        assert mock_serve.called

    @pytest.mark.asyncio
    async def ok_app_test(self):
        testquarts = QuartServer(config)
        client = testquarts._quart_server.test_client()
        response = await client.get('/')
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None
