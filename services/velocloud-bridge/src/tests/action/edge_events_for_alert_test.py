from unittest.mock import Mock

import pytest
from application.actions.edge_events_for_alert import EventEdgesForAlert
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


class TestEventEdgesForAlert:
    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        assert edges_for_alert._event_bus is test_bus
        assert edges_for_alert._velocloud_repository is velocloud_repo
        assert edges_for_alert._logger is mock_logger

    @pytest.mark.asyncio
    async def report_edge_event_ok_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        all_edge_events_response = {"body": "Some edge event info", "status": 200}
        velocloud_repo.get_all_edge_events = CoroutineMock(return_value=all_edge_events_response)
        edge_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.edge.response.123",
            "body": {
                "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
                "limit": 200,
                "filter": ["EDGE_UP"],
            },
        }
        await edges_for_alert.report_edge_event(edge_msg)
        assert velocloud_repo.get_all_edge_events.called
        assert velocloud_repo.get_all_edge_events.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_all_edge_events.call_args[0][1] == edge_msg["body"]["start_date"]

        assert velocloud_repo.get_all_edge_events.call_args[0][2] == edge_msg["body"]["end_date"]
        assert velocloud_repo.get_all_edge_events.call_args[0][3] == edge_msg["body"]["limit"]
        assert velocloud_repo.get_all_edge_events.call_args[0][4] == edge_msg["body"]["filter"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": "Some edge event info",
            "status": 200,
        }
        assert edges_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_event_ok_no_limit_no_filter_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        all_edge_events_response = {"body": "Some edge event info", "status": 200}
        velocloud_repo.get_all_edge_events = CoroutineMock(return_value=all_edge_events_response)
        edge_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.edge.response.123",
            "body": {
                "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
            },
        }
        await edges_for_alert.report_edge_event(edge_msg)
        assert velocloud_repo.get_all_edge_events.called
        assert velocloud_repo.get_all_edge_events.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_all_edge_events.call_args[0][1] == edge_msg["body"]["start_date"]

        assert velocloud_repo.get_all_edge_events.call_args[0][2] == edge_msg["body"]["end_date"]
        assert velocloud_repo.get_all_edge_events.call_args[0][3] is None
        assert velocloud_repo.get_all_edge_events.call_args[0][4] is None
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": "Some edge event info",
            "status": 200,
        }
        assert edges_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_event_ko_missing_keys_in_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        all_edge_events_response = {"body": "Some edge event info", "status": 200}
        velocloud_repo.get_all_edge_events = CoroutineMock(return_value=all_edge_events_response)
        edge_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.edge.response.123",
            "body": {"edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}, "end_date": "now"},
        }
        await edges_for_alert.report_edge_event(edge_msg)
        assert not velocloud_repo.get_all_edge_events.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": 'Must include "edge", "start_date",' ' "end_date" in request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def report_edge_event_no_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        all_edge_events_response = {"body": "Some edge event info", "status": 200}
        velocloud_repo.get_all_edge_events = CoroutineMock(return_value=all_edge_events_response)
        edge_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.edge.response.123",
        }
        await edges_for_alert.report_edge_event(edge_msg)
        assert not velocloud_repo.get_all_edge_events.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": 'Must include "body" in request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def report_edge_event_empty_ko_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges_for_alert = EventEdgesForAlert(test_bus, velocloud_repo, mock_logger)
        edges_for_alert._logger.info = Mock()
        all_edge_events_response = {"body": None, "status": 500}
        velocloud_repo.get_all_edge_events = CoroutineMock(return_value=all_edge_events_response)
        edge_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.edge.response.123",
            "body": {
                "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
            },
        }
        await edges_for_alert.report_edge_event(edge_msg)
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123", "body": None, "status": 500}
        assert edges_for_alert._logger.info.called