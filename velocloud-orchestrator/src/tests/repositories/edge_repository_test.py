from unittest.mock import Mock
from application.repositories.edge_repository import EdgeRepository


class TestEdgeRepository:

    def instance_test(self):
        redis_client = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        assert isinstance(edge_repo, EdgeRepository)
        assert edge_repo._redis_client is redis_client
        assert edge_repo._logger is logger

    def set_edge_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        edge_repo.set_edge("some.edge.id", "some.edge.data")
        assert redis_client.set.called

    def get_edge_ok_test(self):
        redis_client = Mock()
        redis_client.get = Mock(return_value='Some Edge Data')
        redis_client.exists = Mock(return_value=True)
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        redis_data = edge_repo.get_edge("some.edge.id")
        assert redis_client.get.called
        assert redis_data == 'Some Edge Data'

    def get_edge_ko_test(self):
        redis_client = Mock()
        redis_client.get = Mock(return_value='Some Edge Data')
        redis_client.exists = Mock(return_value=False)
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        redis_data = edge_repo.get_edge("some.edge.id")
        assert redis_client.get.called is False
        assert redis_data is None

    def set_current_edge_list_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        edge_repo.set_current_edge_list(["some.edge.id", "other.edge.id"])
        assert redis_client.set.called

    def get_last_edge_list_ok_test(self):
        redis_client = Mock()
        redis_client.get = Mock(return_value=["some.edge.id", "other.edge.id"])
        redis_client.exists = Mock(return_value=True)
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        redis_data = edge_repo.get_last_edge_list()
        assert redis_client.get.called
        assert redis_data == ["some.edge.id", "other.edge.id"]

    def get_edge_list_ko_test(self):
        redis_client = Mock()
        redis_client.get = Mock(return_value=["some.edge.id", "other.edge.id"])
        redis_client.exists = Mock(return_value=False)
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        redis_data = edge_repo.get_last_edge_list()
        assert redis_client.get.called is False
        assert redis_data is None

    def get_keys_test(self):
        redis_client = Mock()
        redis_client.keys = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        edge_repo.get_keys()
        assert redis_client.keys.called
