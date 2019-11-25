import json
import time

from unittest.mock import Mock
from unittest.mock import patch

from application.repositories import edge_repository as edge_repository_module
from application.repositories.edge_repository import EdgeIdentifier
from application.repositories.edge_repository import EdgeRepository


class TestEdgeRepository:

    def instance_test(self):
        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        assert edge_repository._logger is logger
        assert edge_repository._redis_client is redis_client
        assert edge_repository._keys_prefix is keys_prefix

    def remove_all_stored_elements_test(self):
        current_redis_keys = (
            'mettel.velocloud.net|1234|5678',
            'mettel.velocloud.net|1111|2222',
            'mettel.velocloud.net|3333|4444',
        )

        key_prefix = 'test-key'
        logger = Mock()

        redis_client = Mock()
        redis_client.scan_iter = Mock(return_value=current_redis_keys)

        edge_repository = EdgeRepository(logger, redis_client, key_prefix)

        edge_repository.remove_all_stored_elements()

        redis_client.scan_iter.assert_called_once_with(match=f'{key_prefix}*')
        redis_client.delete.assert_called_once_with(*current_redis_keys)

    def add_edge_with_full_id_as_dict_test(self):
        new_edge_host = 'mettel.velocloud.net'
        new_edge_enterprise_id = 1234
        new_edge_id = 5678
        new_edge_full_id = {'host': new_edge_host, 'enterprise_id': new_edge_enterprise_id, 'edge_id': new_edge_id}
        new_edge_status = {'edge_status': {'edges': {'edgeState': 'CONNECTED'}}}

        stored_edge_full_id = 'mettel.velocloud.net|1111|2222'
        stored_edge_value = {
            'addition_timestamp': 123456789,
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status)

        redis_client.set.assert_called_once_with(
            f'{keys_prefix}__{new_edge_host}|{str(new_edge_enterprise_id)}|{str(new_edge_id)}',
            json.dumps({'addition_timestamp': current_timestamp, **new_edge_status}),
            ex=60,
        )

    def add_edge_with_full_id_as_edge_identifier_test(self):
        new_edge_host = 'mettel.velocloud.net'
        new_edge_enterprise_id = 1234
        new_edge_id = 5678
        new_edge_full_id = EdgeIdentifier(host=new_edge_host,
                                          enterprise_id=new_edge_enterprise_id,
                                          edge_id=new_edge_id)
        new_edge_status = {
            'edge_status': {
                'edges': {'edgeState': 'CONNECTED'}
            }
        }

        stored_edge_full_id = 'mettel.velocloud.net|1111|2222'
        stored_edge_value = {
            'addition_timestamp': 123456789,
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status)

        redis_client.set.assert_called_once_with(
            f'{keys_prefix}__{new_edge_host}|{str(new_edge_enterprise_id)}|{str(new_edge_id)}',
            json.dumps({'addition_timestamp': current_timestamp, **new_edge_status}),
            ex=60,
        )

    def add_edge_with_update_existing_edge_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id_str = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_value = {
            'addition_timestamp': 123456789,
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
        }
        currently_stored_edges = {stored_edge_full_id_str: stored_edge_value}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edge_status': {'edges': {'edgeState': 'CONNECTED'}}}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.exists_edge = Mock(return_value=True)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=True)

        redis_client.set.assert_called_once_with(
            f'{keys_prefix}__{stored_edge_full_id_str}',
            json.dumps({
                'addition_timestamp': current_timestamp,
                **new_edge_status,
            }),
            ex=60,
        )

    def add_edge_with_no_update_existing_edge_and_edge_not_actually_existing_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_value = {
            'addition_timestamp': 123456789,
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edge_status': {'edges': {'edgeState': 'CONNECTED'}}}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.exists_edge = Mock(return_value=False)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=False)

        edge_repository.exists_edge.assert_called_once_with(new_edge_full_id)
        redis_client.set.assert_called_once_with(
            f'{keys_prefix}__{stored_edge_full_id}',
            json.dumps({
                'addition_timestamp': current_timestamp,
                **new_edge_status,
            }),
            ex=60,
        )

    def add_edge_with_no_update_existing_edge_and_edge_actually_existing_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_status = {'edge_status': {'edges': {'edgeState': 'OFFLINE'}}, 'addition_timestamp': 123456789}
        currently_stored_edges = {stored_edge_full_id: stored_edge_status}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edges': {'edgeState': 'CONNECTED'}}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.exists_edge = Mock(return_value=True)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=False)

        edge_repository.exists_edge.assert_called_once_with(new_edge_full_id)
        redis_client.set.assert_not_called()

    def add_edge_with_override_of_addition_timestamp_key_test(self):
        new_edge_host = 'mettel.velocloud.net'
        new_edge_enterprise_id = 1234
        new_edge_id = 5678
        new_edge_full_id = {'host': new_edge_host, 'enterprise_id': new_edge_enterprise_id, 'edge_id': new_edge_id}
        new_edge_status = {'addition_timestamp': 999999999, 'edge_status': {'edges': {'edgeState': 'CONNECTED'}}}

        stored_edge_full_id = 'mettel.velocloud.net|1111|2222'
        stored_edge_value = {
            'addition_timestamp': 123456789,
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status)

        redis_client.set.assert_called_once_with(
            f'{keys_prefix}__{new_edge_host}|{str(new_edge_enterprise_id)}|{str(new_edge_id)}',
            json.dumps({'addition_timestamp': 999999999, **new_edge_status}),
            ex=60,
        )

    def get_edge_with_full_id_as_dict_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}
        edge_status = {'edge_status': {'edges': {'edgeState': 'OFFLINE'}}}
        edge_value = {
            'addition_timestamp': 12345678,
            **edge_status,
        }
        edge_value_str = json.dumps(edge_value)

        keys_prefix = 'test-key'
        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=edge_value_str)

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edge = edge_repository.get_edge(edge_full_id)

        redis_client.get.assert_called_once_with(
            f'{keys_prefix}__{edge_host}|{edge_enterprise_id}|{edge_id}'
        )
        assert edge == edge_value

    def get_edge_with_full_id_as_edge_identifier_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}
        edge_identifier = EdgeIdentifier(**edge_full_id)
        edge_status = {'edge_status': {'edges': {'edgeState': 'OFFLINE'}}}
        edge_value = {
            'addition_timestamp': 12345678,
            **edge_status,
        }
        edge_value_str = json.dumps(edge_value)

        keys_prefix = 'test-key'
        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=edge_value_str)

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edge = edge_repository.get_edge(edge_identifier)

        redis_client.get.assert_called_once_with(
            f'{keys_prefix}__{edge_host}|{edge_enterprise_id}|{edge_id}'
        )
        assert edge == edge_value

    def get_edge_with_missing_full_id_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}

        keys_prefix = 'test-key'
        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=None)

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edge = edge_repository.get_edge(edge_full_id)

        redis_client.get.assert_called_once_with(
            f'{keys_prefix}__{edge_host}|{edge_enterprise_id}|{edge_id}'
        )
        assert edge is None

    def get_all_edges_test(self):
        edge_1_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1111
        edge_1_id = 2222
        edge_1_status = {'edge_status': {'edges': {'edgeState': 'OFFLINE'}}}
        edge_1_value = {
            'addition_timestamp': 12345678,
            **edge_1_status,
        }
        edge_1_value_str = json.dumps(edge_1_value)
        edge_1_identifier = EdgeIdentifier(
            host=edge_1_host, enterprise_id=edge_1_enterprise_id, edge_id=edge_1_id)

        edge_2_host = 'mettel.velocloud.net'
        edge_2_enterprise_id = 3333
        edge_2_id = 4444
        edge_2_status = {'edge_status': {'edges': {'edgeState': 'OFFLINE'}}}
        edge_2_value = {
            'addition_timestamp': 12345678,
            **edge_2_status,
        }
        edge_2_value_str = json.dumps(edge_2_value)
        edge_2_identifier = EdgeIdentifier(
            host=edge_2_host, enterprise_id=edge_2_enterprise_id, edge_id=edge_2_id)

        keys_prefix = 'test-key'
        current_redis_keys = [
            f'{keys_prefix}__{edge_1_host}|{edge_1_enterprise_id}|{edge_1_id}',
            f'{keys_prefix}__{edge_2_host}|{edge_2_enterprise_id}|{edge_2_id}',
        ]

        logger = Mock()

        redis_client = Mock()
        redis_client.scan_iter = Mock(return_value=current_redis_keys)
        redis_client.mget = Mock(return_value=[edge_1_value_str, edge_2_value_str])

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edges = edge_repository.get_all_edges()

        redis_client.scan_iter.assert_called_once()
        redis_client.mget.assert_called_once_with(current_redis_keys)
        assert edges == {
            edge_1_identifier: edge_1_value,
            edge_2_identifier: edge_2_value
        }

    def exists_edge_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}
        edge_full_id_str = f'{edge_host}|{edge_enterprise_id}|{edge_id}'

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edge_repository.exists_edge(edge_full_id)

        redis_key = f'{keys_prefix}__{edge_full_id_str}'
        redis_client.exists.assert_called_once_with(redis_key)

    def remove_edge_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}
        edge_full_id_str = f'{edge_host}|{edge_enterprise_id}|{edge_id}'

        keys_prefix = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, keys_prefix)

        edge_repository.remove_edge(edge_full_id)

        redis_key = f'{keys_prefix}__{edge_full_id_str}'
        redis_client.delete.assert_called_once_with(*[redis_key])
