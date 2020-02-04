from application.repositories.edge_dict_repository import EdgeDictRepository
from unittest.mock import Mock
import json


class TestEdgeDictRepository:

    def instance_test(self):
        redis_client = Mock()
        logger = Mock()
        keys_prefix = Mock()
        edge_dict_repo = EdgeDictRepository(redis_client, logger, keys_prefix)
        assert edge_dict_repo._redis_client == redis_client
        assert edge_dict_repo._logger == logger
        assert edge_dict_repo._keys_prefix == keys_prefix

    def set_serial_to_edge_list_test(self):
        logger = Mock()
        key_prefix = 'Test'

        redis_client = Mock()
        redis_client.set = Mock()
        serial = 'VC044'
        edge_list = [{'host': 'metvco', 'enterprise_id': 137, 'edge_id': 134}]
        ttl = 60

        edge_dict_repo = EdgeDictRepository(redis_client, logger, key_prefix)

        edge_dict_repo.set_serial_to_edge_list(serial, edge_list, ttl)

        redis_client.set.assert_called_once_with(f'{key_prefix}_{serial}', json.dumps(edge_list, default=str),
                                                 ex=ttl)

    def get_serial_to_edge_list_ok_test(self):
        logger = Mock()
        key_prefix = 'Test'

        serial = 'VC044'
        edge_list = [{'host': 'metvco', 'enterprise_id': 137, 'edge_id': 134}]

        redis_client = Mock()
        redis_client.get = Mock(return_value=json.dumps(edge_list))

        edge_dict_repo = EdgeDictRepository(redis_client, logger, key_prefix)

        edge_dict_return = edge_dict_repo.get_serial_to_edge_list(serial)

        redis_client.get.assert_called_once_with(f'{key_prefix}_{serial}')

        assert edge_dict_return == edge_list

    def get_serial_to_edge_list_ko_none_test(self):
        logger = Mock()
        key_prefix = 'Test'

        serial = 'VC044'
        edge_list = [{'host': 'metvco', 'enterprise_id': 137, 'edge_id': 134}]

        redis_client = Mock()
        redis_client.get = Mock(return_value=None)

        edge_dict_repo = EdgeDictRepository(redis_client, logger, key_prefix)

        edge_dict_return = edge_dict_repo.get_serial_to_edge_list(serial)

        redis_client.get.assert_called_once_with(f'{key_prefix}_{serial}')

        assert edge_dict_return is None
