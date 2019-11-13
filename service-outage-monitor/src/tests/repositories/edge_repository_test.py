import json
import time

from unittest.mock import Mock
from unittest.mock import patch

from application.repositories import edge_repository as edge_repository_module
from application.repositories.edge_repository import EdgeRepository


class TestEdgeRepository:

    def instance_test(self):
        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)

        assert edge_repository._logger is logger
        assert edge_repository._redis_client is redis_client
        assert edge_repository._root_key is root_key

    def initialize_root_key_test(self):
        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(redis_client, logger, root_key)
        edge_repository.reset_root_key = Mock()

        edge_repository.initialize_root_key()

        edge_repository.reset_root_key.assert_called_once()

    def reset_root_key_test(self):
        root_key_contents = {}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)

        edge_repository.reset_root_key()

        redis_client.set.assert_called_once_with(root_key, root_key_contents)

    def add_edge_test(self):
        new_edge_host = 'mettel.velocloud.net'
        new_edge_enterprise_id = 1234
        new_edge_id = 5678
        new_edge_full_id = {'host': new_edge_host, 'enterprise_id': new_edge_enterprise_id, 'edge_id': new_edge_id}
        new_edge_status = {'edges': {'edgeState': 'CONNECTED'}}

        stored_edge_full_id = 'mettel.velocloud.net|1111|2222'
        stored_edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status)

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps({
                stored_edge_full_id: stored_edge_value,
                f'{new_edge_host}|{str(new_edge_enterprise_id)}|{str(new_edge_id)}': {
                    'edge_status': new_edge_status, 'addition_timestamp': current_timestamp
                }
            }),
            ex=60,
        )

    def add_edge_with_update_existing_edge_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edges': {'edgeState': 'CONNECTED'}}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.exists_edge = Mock(return_value=True)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=True)

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps({
                stored_edge_full_id: {
                    'edge_status': new_edge_status,
                    'addition_timestamp': current_timestamp
                },
            }),
            ex=60,
        )

    def add_edge_with_no_update_existing_edge_and_edge_not_actually_existing_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_value = {
            'edge_status': {'edges': {'edgeState': 'OFFLINE'}},
            'addition_timestamp': 123456789,
        }
        currently_stored_edges = {stored_edge_full_id: stored_edge_value}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edges': {'edgeState': 'CONNECTED'}}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.exists_edge = Mock(return_value=False)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        current_timestamp = time.time()
        time_mock = Mock()
        time_mock.time = Mock(return_value=current_timestamp)
        with patch.object(edge_repository_module, 'time', new=time_mock):
            edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=False)

        edge_repository.exists_edge.assert_called_once_with(new_edge_full_id)
        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps({
                stored_edge_full_id: {
                    'edge_status': new_edge_status,
                    'addition_timestamp': current_timestamp,
                },
            }),
            ex=60,
        )

    def add_edge_with_no_update_existing_edge_and_edge_actually_existing_test(self):
        stored_edge_host = 'mettel.velocloud.net'
        stored_edge_enterprise_id = 1111
        stored_edge_id = 2222

        stored_edge_full_id = f'{stored_edge_host}|{stored_edge_enterprise_id}|{stored_edge_id}'
        stored_edge_status = {'edges': {'edgeState': 'OFFLINE'}, 'addition_timestamp': 123456789}
        currently_stored_edges = {stored_edge_full_id: stored_edge_status}

        new_edge_full_id = {
            'host': stored_edge_host,
            'enterprise_id': stored_edge_enterprise_id,
            'edge_id': stored_edge_id,
        }
        new_edge_status = {'edges': {'edgeState': 'CONNECTED'}}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.exists_edge = Mock(return_value=True)
        edge_repository.get_all_edges = Mock(return_value=currently_stored_edges)

        edge_repository.add_edge(new_edge_full_id, new_edge_status, update_existing=False)

        edge_repository.exists_edge.assert_called_once_with(new_edge_full_id)
        edge_repository.get_all_edges.assert_not_called()
        redis_client.set.assert_not_called()

    def get_all_edges_test(self):
        root_key_contents = {'mettel.velocloud.net|1111|2222': {'edges': {'edgeState': 'OFFLINE'}}}

        root_key = 'test-key'
        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=json.dumps(root_key_contents))

        edge_repository = EdgeRepository(logger, redis_client, root_key)

        edges = edge_repository.get_all_edges()

        redis_client.get.assert_called_once_with(root_key)
        assert edges == root_key_contents

    def exists_edge_test(self):
        edge_host = 'mettel.velocloud.net'
        edge_enterprise_id = 1111
        edge_id = 2222
        edge_full_id = {'host': edge_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}
        edge_full_id_str = f'{edge_host}|{edge_enterprise_id}|{edge_id}'
        root_key_contents = {edge_full_id_str: {'edges': {'edgeState': 'OFFLINE'}}}

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=root_key_contents)

        is_existing_edge = edge_repository.exists_edge(edge_full_id)
        edge_repository.get_all_edges.assert_called_once()
        assert is_existing_edge is True

        edge_repository.get_all_edges.reset_mock()

        is_existing_edge = edge_repository.exists_edge({'host': 'missing', 'enterprise_id': 0, 'edge_id': 0})
        edge_repository.get_all_edges.assert_called_once()
        assert is_existing_edge is False

    def remove_edge_test(self):
        edge_1_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1111
        edge_1_id = 2222
        edge_1_full_id = {'host': edge_1_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}
        edge_1_full_id_str = f'{edge_1_host}|{edge_1_enterprise_id}|{edge_1_id}'
        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}}

        edge_2_host = 'mettel.velocloud.net'
        edge_2_enterprise_id = 3333
        edge_2_id = 4444
        edge_2_full_id_str = f'{edge_2_host}|{edge_2_enterprise_id}|{edge_2_id}'
        edge_2_status = {'edges': {'edgeState': 'CONNECTED'}}

        root_key_contents = {
            edge_1_full_id_str: edge_1_status,
            edge_2_full_id_str: edge_2_status,
        }

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=root_key_contents)

        edge_repository.remove_edge(edge_1_full_id)

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps({
                edge_2_full_id_str: edge_2_status
            }),
        )

    def remove_edge_with_no_existing_edge_test(self):
        edge_1_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1111
        edge_1_id = 2222
        edge_1_full_id_str = f'{edge_1_host}|{edge_1_enterprise_id}|{edge_1_id}'
        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}}

        edge_2_host = 'mettel.velocloud.net'
        edge_2_enterprise_id = 3333
        edge_2_id = 4444
        edge_2_full_id_str = f'{edge_2_host}|{edge_2_enterprise_id}|{edge_2_id}'
        edge_2_status = {'edges': {'edgeState': 'CONNECTED'}}

        root_key_contents = {
            edge_1_full_id_str: edge_1_status,
            edge_2_full_id_str: edge_2_status,
        }

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=root_key_contents)

        edge_repository.remove_edge({'host': 'missing', 'enterprise_id': 0, 'edge_id': 0})

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps(root_key_contents)
        )

    def remove_edge_set_test(self):
        edge_1_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1111
        edge_1_id = 2222
        edge_1_full_id = {'host': edge_1_host, 'enterprise_id': edge_1_enterprise_id, 'edge_id': edge_1_id}
        edge_1_full_id_str = f'{edge_1_host}|{edge_1_enterprise_id}|{edge_1_id}'
        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}}

        edge_2_host = 'mettel.velocloud.net'
        edge_2_enterprise_id = 3333
        edge_2_id = 4444
        edge_2_full_id_str = f'{edge_2_host}|{edge_2_enterprise_id}|{edge_2_id}'
        edge_2_status = {'edges': {'edgeState': 'CONNECTED'}}

        edge_3_host = 'mettel.velocloud.net'
        edge_3_enterprise_id = 5555
        edge_3_id = 6666
        edge_3_full_id = {'host': edge_3_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}
        edge_3_full_id_str = f'{edge_3_host}|{edge_3_enterprise_id}|{edge_3_id}'
        edge_3_status = {'edges': {'edgeState': 'OFFLINE'}}

        root_key_contents = {
            edge_1_full_id_str: edge_1_status,
            edge_2_full_id_str: edge_2_status,
            edge_3_full_id_str: edge_3_status,
        }

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=root_key_contents)

        edge_repository.remove_edge_set(edge_1_full_id, edge_3_full_id)

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps({edge_2_full_id_str: edge_2_status})
        )

    def remove_edge_set_with_no_existing_edges_test(self):
        edge_1_host = 'mettel.velocloud.net'
        edge_1_enterprise_id = 1111
        edge_1_id = 2222
        edge_1_full_id_str = f'{edge_1_host}|{edge_1_enterprise_id}|{edge_1_id}'
        edge_1_status = {'edges': {'edgeState': 'OFFLINE'}}

        edge_2_host = 'mettel.velocloud.net'
        edge_2_enterprise_id = 3333
        edge_2_id = 4444
        edge_2_full_id = {'host': edge_2_host, 'enterprise_id': edge_2_enterprise_id, 'edge_id': edge_2_id}

        edge_3_host = 'mettel.velocloud.net'
        edge_3_enterprise_id = 5555
        edge_3_id = 6666
        edge_3_full_id = {'host': edge_3_host, 'enterprise_id': edge_3_enterprise_id, 'edge_id': edge_3_id}

        root_key_contents = {
            edge_1_full_id_str: edge_1_status,
        }

        root_key = 'test-key'
        logger = Mock()
        redis_client = Mock()

        edge_repository = EdgeRepository(logger, redis_client, root_key)
        edge_repository.get_all_edges = Mock(return_value=root_key_contents)

        edge_repository.remove_edge_set(edge_2_full_id, edge_3_full_id)

        edge_repository.get_all_edges.assert_called_once()
        redis_client.set.assert_called_once_with(
            root_key,
            json.dumps(root_key_contents)
        )
