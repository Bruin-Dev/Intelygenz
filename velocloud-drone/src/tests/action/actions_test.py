import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
import velocloud
from collections import namedtuple
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository


class TestDroneActions:

    def mock_velocloud(self):
        client = Mock()
        client.authenticate = Mock()
        velocloud.ApiClient = Mock(return_value=client)
        all_api_client = Mock()
        all_api_client.edgeGetEdge = Mock(return_value="Some Edge Information")
        all_api_client.api_client.base_path = config.VELOCLOUD_CONFIG['servers'][0]['url']
        velocloud.AllApi = Mock(return_value=all_api_client)

    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        self.mock_velocloud()
        velocloud_repo = VelocloudRepository(config, mock_logger)
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions.event_bus is test_bus
        assert velocloud_repo._logger is mock_logger
        assert actions.velocloud_repository is velocloud_repo

    def process_edge_ok_test(self):
        mock_logger = ()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(return_value="Edge is OK")
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert edge_status == "Edge is OK"
        assert velocloud_repo.get_edge_information.called

    def process_edge_ko_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(side_effect=velocloud.rest.ApiException())
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._logger.exception = Mock()
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert actions._logger.exception.called
        assert edge_status is None
        assert velocloud_repo.get_edge_information.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        actions._logger.error = Mock()
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'FAILING'
        actions._process_edge = Mock(return_value=edge_status)
        await actions.report_edge_status(b'{"SomeIds": "ids"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(SomeIds="ids")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ko'
        assert actions._logger.info.called
        assert actions._logger.error.called

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        actions._logger.error = Mock()
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'CONNECTED'
        actions._process_edge = Mock(return_value=edge_status)
        await actions.report_edge_status(b'{"SomeIds": "ids"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(SomeIds="ids")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ok'
        assert actions._logger.info.called
        assert actions._logger.error.called is False
