from unittest.mock import Mock

import pytest
from application.actions.enterprise_name_list_response import EnterpriseNameList
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


class TestEnterpriseNameListResponse:
    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()
        actions = EnterpriseNameList(test_bus, velocloud_repo, mock_logger)
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert actions._velocloud_repository is velocloud_repo

    @pytest.mark.asyncio
    async def report_enterprise_name_list_response_test(self):
        mock_logger = Mock()
        mock_logger.error = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = EnterpriseNameList(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "request.enterprises.names.123", "body": {"filter": []}}
        enterprises = {"body": [{"enterprise_name": "A Name"}, {"enterprise_name": "Another Name"}], "status": 200}
        velocloud_repo.get_all_enterprise_names = CoroutineMock(return_value=enterprises)
        await actions.enterprise_name_list(msg_dict)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprise_names.called
        assert velocloud_repo.get_all_enterprise_names.call_args[0][0] == msg_dict["body"]
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": enterprises["body"],
            "status": 200,
        }
        assert not actions._logger.error.called

    @pytest.mark.asyncio
    async def report_enterprise_name_list_no_body_response_test(self):
        mock_logger = Mock()
        mock_logger.error = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = EnterpriseNameList(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {
            "request_id": "123",
            "response_topic": "request.enterprises.names.123",
        }
        enterprises = {"body": [{"enterprise_name": "A Name"}, {"enterprise_name": "Another Name"}], "status": 200}
        velocloud_repo.get_all_enterprise_names = CoroutineMock(return_value=enterprises)
        await actions.enterprise_name_list(msg_dict)
        assert not velocloud_repo.get_all_enterprise_names.called
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {
            "request_id": "123",
            "body": 'Must include "body" in request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def report_enterprise_name_list_response_error_500_test(self):
        mock_logger = Mock()
        mock_logger.error = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        actions = EnterpriseNameList(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        msg_dict = {"request_id": "123", "response_topic": "request.enterprises.names.123", "body": {"filter": []}}
        enterprises = {"body": None, "status": 500}
        velocloud_repo.get_all_enterprise_names = CoroutineMock(return_value=enterprises)
        await actions.enterprise_name_list(msg_dict)
        assert actions._logger.info.called
        assert velocloud_repo.get_all_enterprise_names.called
        assert velocloud_repo.get_all_enterprise_names.call_args[0][0] == msg_dict["body"]
        assert test_bus.publish_message.call_args[0][0] == msg_dict["response_topic"]
        assert test_bus.publish_message.call_args[0][1] == {"request_id": "123", "body": None, "status": 500}