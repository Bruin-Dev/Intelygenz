import json
from unittest.mock import Mock

import pytest
from application.actions.edge_id_by_serial_response import SearchForIDsBySerial
from asynctest import CoroutineMock

from igz.packages.eventbus.eventbus import EventBus


class TestEdgeIdBySerialResponse:

    def instance_test(self):
        config = Mock()
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        id_by_serial_repo = Mock()
        actions = SearchForIDsBySerial(config, test_bus, mock_logger, id_by_serial_repo)
        assert actions._config is config
        assert actions._logger is mock_logger
        assert test_bus._logger is mock_logger
        assert actions._event_bus is test_bus
        assert actions._ids_by_serial_repository is id_by_serial_repo

    @pytest.mark.asyncio
    async def search_for_edge_id_ok_test(self):
        config = Mock()
        mock_logger = Mock()

        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()

        edge_id_return = 'Some Edge ID'
        response_topic = "random_topic"
        serial = 'VC05'
        request_id = 123

        request_msg = {'request_id': request_id, "response_topic": response_topic, 'serial': serial}
        response_msg = {'request_id': request_id, "edge_id": edge_id_return, "status": 200}

        id_by_serial_repo = Mock()
        id_by_serial_repo.search_for_edge_id_by_serial = Mock(return_value=edge_id_return)

        actions = SearchForIDsBySerial(config, test_bus, mock_logger, id_by_serial_repo)

        await actions.search_for_edge_id(json.dumps(request_msg))

        id_by_serial_repo.search_for_edge_id_by_serial.assert_called_once_with(serial)

        test_bus.publish_message.assert_awaited_once_with(response_topic, json.dumps(response_msg, default=str))

    @pytest.mark.asyncio
    async def search_for_edge_id_ko_none_test(self):
        config = Mock()
        mock_logger = Mock()

        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()

        edge_id_return = None
        response_topic = "random_topic"
        serial = 'VC05'
        request_id = 123

        request_msg = {'request_id': request_id, "response_topic": response_topic, 'serial': serial}
        response_msg = {'request_id': request_id, "edge_id": edge_id_return, "status": 204}

        id_by_serial_repo = Mock()
        id_by_serial_repo.search_for_edge_id_by_serial = Mock(return_value=edge_id_return)

        actions = SearchForIDsBySerial(config, test_bus, mock_logger, id_by_serial_repo)

        await actions.search_for_edge_id(json.dumps(request_msg))

        id_by_serial_repo.search_for_edge_id_by_serial.assert_called_once_with(serial)

        test_bus.publish_message.assert_awaited_once_with(response_topic, json.dumps(response_msg, default=str))

    @pytest.mark.asyncio
    async def search_for_edge_id_ok_exception_test(self):
        config = Mock()
        mock_logger = Mock()

        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()

        edge_id_return = Exception()
        response_topic = "random_topic"
        serial = 'VC05'
        request_id = 123

        request_msg = {'request_id': request_id, "response_topic": response_topic, 'serial': serial}
        response_msg = {'request_id': request_id, "edge_id": edge_id_return, "status": 500}

        id_by_serial_repo = Mock()
        id_by_serial_repo.search_for_edge_id_by_serial = Mock(return_value=edge_id_return)

        actions = SearchForIDsBySerial(config, test_bus, mock_logger, id_by_serial_repo)

        await actions.search_for_edge_id(json.dumps(request_msg))

        id_by_serial_repo.search_for_edge_id_by_serial.assert_called_once_with(serial)

        test_bus.publish_message.assert_awaited_once_with(response_topic, json.dumps(response_msg, default=str))
