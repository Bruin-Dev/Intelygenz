import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.edges_for_alert import EdgesForAlert
from igz.packages.eventbus.eventbus import EventBus
import json
import asyncio


class TestEdgesForAlert:

    def instance_test(self):
        logger = Mock()
        event_bus = EventBus(logger=logger)
        velocloud_repository = Mock()
        edges_for_alert = EdgesForAlert(event_bus, velocloud_repository, logger)
        assert edges_for_alert._event_bus is event_bus
        assert edges_for_alert._velocloud_repository is velocloud_repository
        assert edges_for_alert._logger is logger

    @pytest.mark.asyncio
    async def report_edge_list_ok_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "edge.list.response.123", "filter": []}
        msg = json.dumps(msg_dict)
        edges = ["EdgeIds1"]
        velocloud_repo.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        velocloud_repo.get_alert_information = Mock()
        await edges_for_alert.report_edge_list(msg)
        assert edges_for_alert._logger.info.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.called
        assert velocloud_repo.get_all_enterprises_edges_with_host.call_args[0][0] == msg_dict
        assert velocloud_repo.get_alert_information.call_args[0][0] == edges[0]

    @pytest.mark.asyncio
    async def gather_and_send_edge_list_test(self):
        edge_data = [{"edges": {"edges": "Some edge data", "enterprise": "FakeCorp"}}]
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        future = asyncio.Future()
        future.set_result(edge_data)
        futures_edges = [future]

        edges_response = json.dumps(
            {"request_id": "123",
             "edges": [[{"edges": {"edges": "Some edge data", "enterprise": "FakeCorp"}}]],
             "status": 200})

        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EdgesForAlert(test_bus, velocloud_repo, mock_logger)

        await edges_for_alert._gather_and_send_edge_list(futures_edges, request_id, response_topic)
        assert test_bus.publish_message.call_args[0][0] == response_topic
        assert test_bus.publish_message.call_args[0][1] == edges_response
