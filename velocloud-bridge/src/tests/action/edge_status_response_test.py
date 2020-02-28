import json
from unittest.mock import Mock

import pytest
from application.actions.edge_status_response import ReportEdgeStatus
from asynctest import CoroutineMock

from config import testconfig as config
from igz.packages.eventbus.eventbus import EventBus


class TestEdgeStatusResponse:

    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        assert actions._configs is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert actions._velocloud_repository is velocloud_repo

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = {"body": "TEST", "status_code": 200}
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        edge_information = {"body": [], "status_code": 200}
        velocloud_repo.get_edge_information = Mock(return_value=edge_information)
        link_information = {"body": [{"link_data": "STABLE", "linkId": "123"}], "status_code": 200}
        velocloud_repo.get_link_information = Mock(return_value=link_information)
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "body": {"edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}}
        await actions.report_edge_status(edge_msg)
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body": {
                                                                "edge_id": {"host": "host", "enterprise_id": "2",
                                                                            "edge_id": "1"},
                                                                "edge_info": {
                                                                    "enterprise_name": enterprise_info["body"],
                                                                    "edges": [],
                                                                    "links":
                                                                        [{"link_data": "STABLE",
                                                                          "linkId": "123"}
                                                                         ]}
                                                            },
                                                            "status": 200}
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ok_status_link_interval_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = {"body": "TEST", "status_code": 200}
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        edge_information = {"body": [], "status_code": 200}
        velocloud_repo.get_edge_information = Mock(return_value=edge_information)
        link_information = {"body": [{"link_data": "STABLE", "linkId": "123"}], "status_code": 200}
        velocloud_repo.get_link_information = Mock(return_value=link_information)
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "body": {
                        "edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"},
                        "interval": {"end": "now", "start": "15 mins ago"}}
                    }
        await actions.report_edge_status(edge_msg)
        assert velocloud_repo.get_enterprise_information.called
        assert velocloud_repo.get_enterprise_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_edge_information.called
        assert velocloud_repo.get_edge_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_link_information.called
        assert velocloud_repo.get_link_information.call_args[0][0] == edge_msg["body"]["edge"]
        assert velocloud_repo.get_link_information.call_args[0][1] == edge_msg["body"]["interval"]
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body":
                                                                {
                                                                    "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                "edge_id": "1"},
                                                                    "edge_info": {
                                                                        "enterprise_name": enterprise_info["body"],
                                                                        "edges": [],
                                                                        "links":
                                                                            [{"link_data": "STABLE",
                                                                              "linkId": "123"}
                                                                             ]}
                                                                },
                                                            "status": 200}
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_ko_empty_status_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        enterprise_info = {"body": "TEST", "status_code": 200}
        velocloud_repo.get_enterprise_information = Mock(return_value=enterprise_info)
        edge_information = {"body": [], "status_code": 200}
        velocloud_repo.get_edge_information = Mock(return_value=edge_information)
        link_information = {"body": None, "status_code": 500}
        velocloud_repo.get_link_information = Mock(return_value=link_information)
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123",
                    "body": {"edge": {"host": "host", "enterprise_id": "2", "edge_id": "1"}}}
        await actions.report_edge_status(edge_msg)
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body":
                                                                {
                                                                    "edge_id": {"host": "host", "enterprise_id": "2",
                                                                                "edge_id": "1"},
                                                                    "edge_info": {
                                                                        "enterprise_name": enterprise_info["body"],
                                                                        "edges": [],
                                                                        "links": None}
                                                                },
                                                            "status": 500}
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def report_edge_status_empty_msg_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = ReportEdgeStatus(config, test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        velocloud_repo.get_enterprise_information = Mock()
        velocloud_repo.get_edge_information = Mock()
        velocloud_repo.get_link_information = Mock()
        edge_msg = {"request_id": "123", "response_topic": "edge.status.response.123"}

        await actions.report_edge_status(edge_msg)
        assert not velocloud_repo.get_enterprise_information.called
        assert not velocloud_repo.get_edge_information.called
        assert not velocloud_repo.get_link_information.called
        assert test_bus.publish_message.called
        assert test_bus.publish_message.call_args[0][0] == edge_msg["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123",
                                                            "body": None,
                                                            "status": 500}
        assert actions._logger.info.called
