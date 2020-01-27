from application.repositories.edge_dict_repository import EdgeDictRepository
from unittest.mock import Mock
import json


class TestEdgeDictRepository:

    def instance_test(self):
        redis_client = Mock()
        logger = Mock()
        edge_dict_repo = EdgeDictRepository(redis_client, logger)
        assert edge_dict_repo._redis_client == redis_client
        assert edge_dict_repo._logger == logger

    def set_current_edge_dict_test(self):
        logger = Mock()

        redis_client = Mock()
        redis_client.set = Mock()
        edge_dict = {'VC044': {'host': 'metvco', 'enterprise_id': 137, 'edge_id': 134}}

        edge_dict_repo = EdgeDictRepository(redis_client, logger)

        edge_dict_repo.set_current_edge_dict(edge_dict)

        redis_client.set.assert_called_once_with("edge_dict", json.dumps(edge_dict, default=str))

    def get_last_current_edge_ok_dict_test(self):
        logger = Mock()

        edge_dict = {'VC044': {'host': 'metvco', 'enterprise_id': 137, 'edge_id': 134}}

        redis_client = Mock()
        redis_client.get = Mock(return_value=json.dumps(edge_dict))

        edge_dict_repo = EdgeDictRepository(redis_client, logger)

        edge_dict_return = edge_dict_repo.get_last_edge_dict()

        redis_client.get.assert_called_once_with("edge_dict")

        assert edge_dict_return == edge_dict

    def get_last_current_edge_ko_none_dict_test(self):
        logger = Mock()

        redis_client = Mock()
        redis_client.get = Mock(return_value=None)

        edge_dict_repo = EdgeDictRepository(redis_client, logger)

        edge_dict_return = edge_dict_repo.get_last_edge_dict()

        redis_client.get.assert_called_once_with("edge_dict")

        assert edge_dict_return is None
