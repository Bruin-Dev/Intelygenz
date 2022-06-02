from unittest.mock import Mock

import pytest
from application.actions.links_configuration import LinksConfiguration
from asynctest import CoroutineMock
from igz.packages.eventbus.eventbus import EventBus


class TestLinksConfiguration:
    def instance_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        test_bus = EventBus(storage_manager, logger=mock_logger)
        velocloud_repo = Mock()

        links_configuration_instance = LinksConfiguration(test_bus, velocloud_repo, mock_logger)

        assert links_configuration_instance._event_bus is test_bus
        assert links_configuration_instance._velocloud_repository is velocloud_repo
        assert links_configuration_instance._logger is mock_logger

    @pytest.mark.asyncio
    async def links_configuration_ok_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        event_bus.publish_message = CoroutineMock()
        velocloud_repository = Mock()
        links_configuration_response = {"body": "Some edge config module", "status": 200}
        velocloud_repository.get_links_configuration = CoroutineMock(return_value=links_configuration_response)
        links_configuration = LinksConfiguration(event_bus, velocloud_repository, mock_logger)
        links_configuration._logger.info = Mock()

        request = {
            "request_id": 1234,
            "response_topic": "request.edge.config.modules",
            "body": {"host": "metvco02.mettel.net", "enterprise_id": 1, "edge_id": 4784},
        }

        await links_configuration.links_configuration(request)
        assert links_configuration._velocloud_repository.get_links_configuration.called
        assert links_configuration._event_bus.publish_message.called
        assert links_configuration._event_bus.publish_message.call_args[0][1] == {
            "request_id": 1234,
            "body": "Some edge config module",
            "status": 200,
        }

    @pytest.mark.asyncio
    async def links_configuration_ko_missing_keys_in_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        event_bus.publish_message = CoroutineMock()
        velocloud_repository = Mock()
        links_configuration = LinksConfiguration(event_bus, velocloud_repository, mock_logger)
        links_configuration._logger.info = Mock()
        request = {
            "request_id": 1234,
            "response_topic": "request.edge.config.modules",
            "body": {"host": "metvco02.mettel.net", "edge_id": 4784},
        }
        await links_configuration.links_configuration(request)
        assert not links_configuration._velocloud_repository.get_config.called
        assert links_configuration._event_bus.publish_message.called
        assert links_configuration._event_bus.publish_message.call_args[0][0] == request["response_topic"]
        assert links_configuration._event_bus.publish_message.call_args[0][1] == {
            "request_id": 1234,
            "body": 'You must specify {..."body": {"host", "enterprise_id", "edge_id"}...} in the request',
            "status": 400,
        }

    @pytest.mark.asyncio
    async def links_configuration_ko_not_body_test(self):
        mock_logger = Mock()
        storage_manager = Mock()
        event_bus = EventBus(storage_manager, logger=mock_logger)
        event_bus.publish_message = CoroutineMock()
        velocloud_repository = Mock()
        links_configuration = LinksConfiguration(event_bus, velocloud_repository, mock_logger)
        links_configuration._logger.info = Mock()
        request = {
            "request_id": 1234,
            "response_topic": "request.edge.config.modules",
        }
        await links_configuration.links_configuration(request)
        assert not links_configuration._velocloud_repository.get_config.called
        assert links_configuration._event_bus.publish_message.called
        assert links_configuration._event_bus.publish_message.call_args[0][0] == request["response_topic"]
        assert links_configuration._event_bus.publish_message.call_args[0][1] == {
            "request_id": 1234,
            "body": 'Must include "body" in request',
            "status": 400,
        }
