from unittest.mock import Mock

import pytest
from application.clients.ids_by_serial_client import IDsBySerialClient
from asynctest import CoroutineMock
from pytest import raises

from config import testconfig


class TestIDsBySerialClient:

    def instance_test(self):
        config = testconfig
        mock_logger = Mock()
        velo_client = Mock()
        edge_dict_repo = Mock()
        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client, edge_dict_repo)
        assert id_by_serial_client._config == config.VELOCLOUD_CONFIG
        assert id_by_serial_client._logger == mock_logger
        assert id_by_serial_client._velocloud_client == velo_client
        assert id_by_serial_client._edge_dict_repository == edge_dict_repo

    @pytest.mark.asyncio
    async def create_id_by_serial_dict_test(self):
        config = testconfig
        mock_logger = Mock()

        serial = 'VC0123'
        ttl = testconfig.VELOCLOUD_CONFIG['ids_by_serial_cache_ttl']
        serial_dict = {serial: [{'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}]}
        velo_client = Mock()
        velo_client.get_all_enterprises_edges_with_host_by_serial = CoroutineMock(return_value=serial_dict)

        edge_dict_repo = Mock()
        edge_dict_repo.set_serial_to_edge_list = Mock()

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client, edge_dict_repo)

        await id_by_serial_client.create_id_by_serial_dict()

        edge_dict_repo.set_serial_to_edge_list.called_once_with(serial, serial_dict[serial], ttl)

    @pytest.mark.asyncio
    async def search_for_edge_id_by_serial_ok_test(self):
        config = testconfig
        mock_logger = Mock()
        velo_client = Mock()

        serial = 'VC0123'
        edge_id = {'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}

        edge_repo = Mock()
        edge_repo.get_serial_to_edge_list = Mock(return_value=[edge_id])

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client, edge_repo)

        found_edge_id = await id_by_serial_client.search_for_edge_id_by_serial(serial)

        assert found_edge_id == [edge_id]

    @pytest.mark.asyncio
    async def search_for_edge_id_by_serial_ko_test(self):
        config = testconfig
        mock_logger = Mock()
        mock_logger.error = Mock()
        velo_client = Mock()

        serial = 'VC0123'
        edge_id = {'host': 'some_host', 'edge_id': 123, 'enterprise_id': 432}

        edge_repo = Mock()
        edge_repo.get_serial_to_edge_list = Mock(return_value=None)

        id_by_serial_client = IDsBySerialClient(config, mock_logger, velo_client, edge_repo)

        with raises(Exception):
            found_edge_id = await id_by_serial_client.search_for_edge_id_by_serial(serial)
            mock_logger.error.called()
            assert found_edge_id == ''
