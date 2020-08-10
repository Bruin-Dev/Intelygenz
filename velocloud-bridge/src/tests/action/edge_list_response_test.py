import json
from unittest.mock import Mock

import pytest
from application.actions.edge_list_response import ReportEdgeList
from asynctest import CoroutineMock

from config import testconfig as config
from igz.packages.eventbus.eventbus import EventBus


class TestEdgeListResponse:

    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        assert actions._configs is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert actions._velocloud_repository is velocloud_repo

    @pytest.mark.asyncio
    async def report_edge_list_ok_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123", 'body': {"filter": []}}
        edges = {"body": ["task1", "task2"], "status": 200}
        velocloud_repo.get_all_enterprises_edges_with_host = CoroutineMock(return_value=edges)
        await actions.report_edge_list(msg_dict)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.call_args[0][0] == msg_dict['body']
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body": edges["body"],
                                                            "status": 200}

    @pytest.mark.asyncio
    async def report_edge_list_empty_ko_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123", 'body': {"filter": []}}
        edges = {"body": None, "status": 500}
        velocloud_repo.get_all_enterprises_edges_with_host = CoroutineMock(return_value=edges)
        await actions.report_edge_list(msg_dict)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.call_args[0][0] == msg_dict['body']
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body": None,
                                                            "status": 500}

    @pytest.mark.asyncio
    async def report_edge_list_empty_msg_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeList(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123"}
        velocloud_repo.get_all_enterprises_edges_with_host = CoroutineMock()

        await actions.report_edge_list(msg_dict)
        assert actions._logger.info.called
        assert not velocloud_repo.get_all_enterprises_edges_with_host.called
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body": 'Must include "body" in request',
                                                            "status": 400}
