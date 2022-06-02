import json
from unittest.mock import Mock

import pytest
from application.actions.enterprise_events_for_alert import EventEnterpriseForAlert
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


class TestEventEnterpriseForAlert:
    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        assert enterprise_for_alert._event_bus is test_bus
        assert enterprise_for_alert._velocloud_repository is velocloud_repo
        assert enterprise_for_alert._logger is mock_logger

    @pytest.mark.asyncio
    async def report_enterprise_event_ok_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        enterprise_for_alert._logger.info = Mock()
        all_enterprise_events_response = {"body": "Some enterprise event info", "status": 200}
        velocloud_repo.get_all_enterprise_events = CoroutineMock(return_value=all_enterprise_events_response)
        enterprise_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.enterprise.response.123",
            "body": {
                "host": "host",
                "enterprise_id": "2",
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
                "limit": 200,
                "filter": ["EDGE_UP"],
            },
        }
        await enterprise_for_alert.report_enterprise_event(enterprise_msg)
        assert velocloud_repo.get_all_enterprise_events.called
        assert velocloud_repo.get_all_enterprise_events.call_args[0][0] == enterprise_msg["body"]["enterprise_id"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][1] == enterprise_msg["body"]["host"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][2] == enterprise_msg["body"]["start_date"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][3] == enterprise_msg["body"]["end_date"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][4] == enterprise_msg["body"]["limit"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][5] == enterprise_msg["body"]["filter"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == enterprise_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": "Some enterprise event info",
            "status": 200,
        }
        assert enterprise_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_enterprise_event_ok_no_limit_no_filter_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        enterprise_for_alert._logger.info = Mock()
        all_enterprise_events_response = {"body": "Some enterprise event info", "status": 200}
        velocloud_repo.get_all_enterprise_events = CoroutineMock(return_value=all_enterprise_events_response)
        enterprise_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.enterprise.response.123",
            "body": {
                "host": "host",
                "enterprise_id": "2",
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
            },
        }
        await enterprise_for_alert.report_enterprise_event(enterprise_msg)
        assert velocloud_repo.get_all_enterprise_events.called
        assert velocloud_repo.get_all_enterprise_events.call_args[0][0] == enterprise_msg["body"]["enterprise_id"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][1] == enterprise_msg["body"]["host"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][2] == enterprise_msg["body"]["start_date"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][3] == enterprise_msg["body"]["end_date"]
        assert velocloud_repo.get_all_enterprise_events.call_args[0][4] is None
        assert velocloud_repo.get_all_enterprise_events.call_args[0][5] is None
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == enterprise_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": "Some enterprise event info",
            "status": 200,
        }
        assert enterprise_for_alert._logger.info.called

    @pytest.mark.asyncio
    async def report_enterprise_event_ko_missing_keys_in_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        enterprise_for_alert._logger.info = Mock()
        all_enterprise_events_response = {"body": "Some enterprise event info", "status": 200}
        velocloud_repo.get_all_enterprise_events = CoroutineMock(return_value=all_enterprise_events_response)
        enterprise_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.enterprise.response.123",
            "body": {"host": "host", "enterprise_id": "2", "end_date": "now"},
        }
        await enterprise_for_alert.report_enterprise_event(enterprise_msg)
        assert not velocloud_repo.get_all_enterprise_events.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == enterprise_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": 'Must include "enterprise_id", "host", ' '"start_date", "end_date" in request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def report_enterprise_event_no_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        enterprise_for_alert._logger.info = Mock()
        all_enterprise_events_response = {"body": "Some enterprise event info", "status": 200}
        velocloud_repo.get_all_enterprise_events = CoroutineMock(return_value=all_enterprise_events_response)
        enterprise_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.enterprise.response.123",
        }
        await enterprise_for_alert.report_enterprise_event(enterprise_msg)
        assert not velocloud_repo.get_all_enterprise_events.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == enterprise_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": 'Must include "body" in request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def report_enterprise_event_empty_ko_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        enterprise_for_alert = EventEnterpriseForAlert(test_bus, velocloud_repo, mock_logger)
        enterprise_for_alert._logger.info = Mock()
        all_enterprise_events_response = {"body": None, "status": 500}
        velocloud_repo.get_all_enterprise_events = CoroutineMock(return_value=all_enterprise_events_response)
        enterprise_msg = {
            "request_id": "123",
            "response_topic": "alert.request.event.enterprise.response.123",
            "body": {
                "host": "host",
                "enterprise_id": "2",
                "start_date": "2019-07-26 14:19:45.334427",
                "end_date": "now",
            },
        }
        await enterprise_for_alert.report_enterprise_event(enterprise_msg)
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == enterprise_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123", "body": None, "status": 500}
        assert enterprise_for_alert._logger.info.called
