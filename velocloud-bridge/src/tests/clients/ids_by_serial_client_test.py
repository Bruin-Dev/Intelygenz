from unittest.mock import Mock

from application.clients.ids_by_serial_client import IDsBySerialClient
from pytest import raises

from config import testconfig


class TestIDsBySerialClient:

    def instance_test(self):
        config = testconfig
        mock_logger = Mock()
        velo_client = Mock()
        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client)
        assert id_by_serial_client._config == config.VELOCLOUD_CONFIG
        assert id_by_serial_client._logger == mock_logger
        assert id_by_serial_client._velocloud_client == velo_client
        assert id_by_serial_client._id_by_serial_dict == {}

    def create_id_by_serial_dict_test(self):
        config = testconfig
        mock_logger = Mock()

        serial_dict = {'VC0123': {'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}}
        velo_client = Mock()
        velo_client.get_all_enterprises_edges_with_host_by_serial = Mock(return_value=serial_dict)

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client)

        id_by_serial_client.create_id_by_serial_dict()

        assert id_by_serial_client._id_by_serial_dict == serial_dict

    def search_for_edge_id_by_serial_ok_test(self):
        config = testconfig
        mock_logger = Mock()
        velo_client = Mock()

        serial = 'VC0123'
        edge_id = {'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client)
        id_by_serial_client._id_by_serial_dict = {serial: edge_id}

        found_edge_id = id_by_serial_client.search_for_edge_id_by_serial(serial)

        assert found_edge_id == edge_id

    def search_for_edge_id_by_serial_ko_test(self):
        config = testconfig
        mock_logger = Mock()
        mock_logger.error = Mock()
        velo_client = Mock()

        serial = 'VC0123'
        edge_id = {'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client)
        id_by_serial_client._id_by_serial_dict = {'VC0143': edge_id}

        with raises(Exception):
            found_edge_id = id_by_serial_client.search_for_edge_id_by_serial(serial)
            mock_logger.error.called()
            assert found_edge_id == ''
