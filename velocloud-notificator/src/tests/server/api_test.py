from application.server.api import quart_server
import pytest


class Testapi:

    @pytest.mark.asyncio
    async def ok_app_test(self):
        client = quart_server.test_client()
        response = await client.get('/')
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None
