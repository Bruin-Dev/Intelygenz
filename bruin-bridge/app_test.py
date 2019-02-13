import unittest
#TODO try to fix imports in order to work with unittest too
import app
from unittest.mock import MagicMock
from asgiref.sync import async_to_sync, sync_to_async
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class NATSClient(unittest.TestCase):
    @async_to_sync
    async def test_is_instance_of(self):
        NATS.connect = sync_to_async(MagicMock())
        STAN.connect = sync_to_async(MagicMock())
        nats_connector = app.NATSConnector()
        await nats_connector.connect_to_nats()
        self.assertIsInstance(nats_connector.nc, NATS)
        self.assertIsInstance(nats_connector.sc, STAN)

    # def test_project_is_structured(self):
    #     self.assertEqual("Project structure", "FALSE")


if __name__ == '__main__':
    unittest.main()
