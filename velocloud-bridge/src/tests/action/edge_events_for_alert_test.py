import pytest
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.edge_events_for_alert import EventEdgesForAlert
from igz.packages.eventbus.eventbus import EventBus
import json


class TestEventEdgesForAlert:

    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        assert edges_for_alert._event_bus is test_bus
        assert edges_for_alert._velocloud_repository is velocloud_repo
        assert edges_for_alert._logger is mock_logger

    @pytest.mark.asyncio
    async def report_edge_event_ok_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        velocloud_repo.get_all_edge_events = Mock(return_value="Some edge event info")
        edge_msg = {"request_id": "123", "response_topic": "alert.request.event.edge.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "start_date": "2019-07-26 14:19:45.334427",
                    "end_date": "now",
                    "limit": 200}
        await edges_for_alert.report_edge_event(json.dumps(edge_msg, default=str))
        assert velocloud_repo.get_all_edge_events.called
        assert velocloud_repo.get_all_edge_events.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_all_edge_events.call_args[0][1] == edge_msg["start_date"]

        assert velocloud_repo.get_all_edge_events.call_args[0][2] == edge_msg["end_date"]
        assert velocloud_repo.get_all_edge_events.call_args[0][3] == edge_msg["limit"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "events": "Some edge event info",
                                                                       "status": 200})
        assert edges_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_event_ok_no_limit_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        velocloud_repo.get_all_edge_events = Mock(return_value="Some edge event info")
        edge_msg = {"request_id": "123", "response_topic": "alert.request.event.edge.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "start_date": "2019-07-26 14:19:45.334427",
                    "end_date": "now"}
        await edges_for_alert.report_edge_event(json.dumps(edge_msg, default=str))
        assert velocloud_repo.get_all_edge_events.called
        assert velocloud_repo.get_all_edge_events.call_args[0][0] == edge_msg["edge"]
        assert velocloud_repo.get_all_edge_events.call_args[0][1] == edge_msg["start_date"]

        assert velocloud_repo.get_all_edge_events.call_args[0][2] == edge_msg["end_date"]
        assert velocloud_repo.get_all_edge_events.call_args[0][3] is None
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "events": "Some edge event info",
                                                                       "status": 200})
        assert edges_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_event_empty_ko_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        velocloud_repo.get_all_edge_events = Mock(return_value=None)
        edge_msg = {"request_id": "123", "response_topic": "alert.request.event.edge.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "start_date": "2019-07-26 14:19:45.334427",
                    "end_date": "now"}
        await edges_for_alert.report_edge_event(json.dumps(edge_msg, default=str))
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "events": None,
                                                                       "status": 204})
        assert edges_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_event_exception_ko_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        velocloud_repo.get_all_edge_events = Mock(return_value=Exception())
        edge_msg = {"request_id": "123", "response_topic": "alert.request.event.edge.response.123",
                    "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                    "start_date": "2019-07-26 14:19:45.334427",
                    "end_date": "now"}
        await edges_for_alert.report_edge_event(json.dumps(edge_msg, default=str))
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == json.dumps({"request_id": "123",
                                                                       "events": "",
                                                                       "status": 500})
        assert edges_for_alert._logger.info.called
