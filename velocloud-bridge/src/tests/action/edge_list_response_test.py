import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.edge_list_response import ReportEdgeList
from igz.packages.eventbus.eventbus import EventBus
from config import testconfig as config
from application.repositories.velocloud_repository import VelocloudRepository
from velocloud_client.client.velocloud_client import VelocloudClient
import json


class TestEdgeListResponse:

    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_velocloud_client = VelocloudClient(config)
        velocloud_repo = VelocloudRepository(config, mock_logger, test_velocloud_client)
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        assert actions._configs is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert velocloud_repo._logger is mock_logger
        assert actions._velocloud_repository is velocloud_repo

    @pytest.mark.asyncio
    async def report_edge_list_ok_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123", "filter": []}
        msg = json.dumps(msg_dict)
        edges = ["task1", "task2"]
        velocloud_repo.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        await actions.report_edge_list(msg)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.call_args[0][0] == msg_dict
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edges": edges,
                                                                       "status": 200})

    @pytest.mark.asyncio
    async def report_edge_list_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123", "filter": []}
        msg = json.dumps(msg_dict)
        velocloud_repo.get_all_enterprises_edges_with_host = Mock(return_value=None)
        await actions.report_edge_list(msg)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.call_args[0][0] == msg_dict
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "edges": None,
                                                                       "status": 500})
