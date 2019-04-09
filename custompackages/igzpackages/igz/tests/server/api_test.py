from igz.packages.server.api import QuartServer
import pytest
from igz.config import testconfig as config
from quart_openapi import Pint


class Testapi:

    def instantiation_test(self):
        testquarts = QuartServer(config)
        assert testquarts._title == config.QUART_CONFIG['title']
        assert testquarts._port == config.QUART_CONFIG['port']
        assert isinstance(testquarts._quart_server, Pint) is True

    @pytest.mark.asyncio
    async def ok_app_test(self):
        testquarts = QuartServer(config)
        client = testquarts._quart_server.test_client()
        response = await client.get('/')
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None
