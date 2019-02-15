import pytest
from ..application.clients.natssclient import NATSSClient
from unittest.mock import MagicMock
from asgiref.sync import async_to_sync, sync_to_async
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class NATSSClientTest():
    @async_to_sync
    async def test_is_instance_of(self):
        NATS.connect = sync_to_async(MagicMock())
        STAN.connect = sync_to_async(MagicMock())
        nats_s_client = NATSSClient()
        await nats_s_client.connect_to_nats()
        assert isinstance(nats_s_client.nc, NATS)
        assert isinstance(nats_s_client.sc, STAN)

    # @pytest.mark.xfail(reason="Will fail as a reminder of preeliminar project structure")
    # def test_project_is_structured(self):
    #     assert "Project structure" == "FALSE"
