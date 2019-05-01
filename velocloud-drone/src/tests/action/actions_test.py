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
        test_prometheus = Mock()
        self.mock_velocloud()
        velocloud_repo = VelocloudRepository(config, mock_logger)
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        assert actions._configs is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert velocloud_repo._logger is mock_logger
        assert actions._velocloud_repository is velocloud_repo
        assert actions._prometheus_repository is test_prometheus

    def process_edge_ok_test(self):
        mock_logger = ()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(return_value="Edge is OK")
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert edge_status == "Edge is OK"
        assert velocloud_repo.get_edge_information.called

    def process_edge_ko_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        velocloud_repo.get_edge_information = Mock(side_effect=velocloud.rest.ApiException())
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._logger.exception = Mock()
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        edge_status = actions._process_edge(edgeis)
        assert actions._logger.exception.called
        assert edge_status is None
        assert velocloud_repo.get_edge_information.called

    def process_link_ok_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        velocloud_repo.get_link_information = Mock(return_value="Link is OK")
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        link_status = actions._process_link(edgeis)
        assert link_status == "Link is OK"
        assert velocloud_repo.get_link_information.called

    def process_link_ko_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        velocloud_repo.get_link_information = Mock(side_effect=velocloud.rest.ApiException())
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._logger.exception = Mock()
        edgeis = dict(host="somehost", enterpriseId=19, id=99)
        link_status = actions._process_link(edgeis)
        assert actions._logger.exception.called
        assert link_status is None
        assert velocloud_repo.get_link_information.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        test_prometheus = Mock()
        velocloud_repo = Mock()
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._logger.info = Mock()
        actions._logger.error = Mock()
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'FAILING'
        link_status = []
        actions._prometheus_repository.inc = Mock()
        actions._process_edge = Mock(return_value=edge_status)
        actions._process_link = Mock(return_value=link_status)
        enterprise_info = Mock()
        enterprise_info._name = Mock()
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        await actions.report_edge_status(b'{"enterpriseId": "ids", "host": "host"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(enterpriseId="ids", host="host")
        assert actions._process_link.called
        assert actions._process_link.call_args[0][0] == dict(enterpriseId="ids", host="host")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ko'
        assert actions._logger.info.called
        assert actions._logger.error.called
        assert actions._prometheus_repository.inc.called

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        test_prometheus = Mock()
        velocloud_repo = Mock()
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._logger.info = Mock()
        actions._logger.error = Mock()
        edge_status = namedtuple("edge_status", [])
        edge_status._edgeState = 'CONNECTED'
        link_status = 'OKAY'
        enterprise_info = Mock()
        enterprise_info._name = Mock()
        actions._prometheus_repository.inc = Mock()
        actions._process_edge = Mock(return_value=edge_status)
        actions._process_link = Mock(return_value=link_status)
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        await actions.report_edge_status(b'{"enterpriseId": "ids", "host": "host"}')
        assert test_bus.publish_message.called
        assert actions._process_edge.called
        assert actions._process_edge.call_args[0][0] == dict(enterpriseId="ids", host="host")
        assert test_bus.publish_message.call_args[0][0] == 'edge.status.ok'
        assert actions._logger.info.called
        assert actions._logger.error.called is False
        assert actions._prometheus_repository.inc.called

    def start_prometheus_metrics_server_test(self):
        mock_logger = ()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._prometheus_repository.start_prometheus_metrics_server = Mock()
        actions.start_prometheus_metrics_server()
        assert actions._prometheus_repository.start_prometheus_metrics_server.called is True

    @pytest.mark.asyncio
    async def reset_counter_test(self):
        mock_logger = ()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus = Mock()
        velocloud_repo = Mock()
        actions = Actions(config, test_bus, velocloud_repo, mock_logger, test_prometheus)
        actions._prometheus_repository.reset_counter = CoroutineMock()
        await actions.reset_counter()
        assert actions._prometheus_repository.reset_counter.called is True
