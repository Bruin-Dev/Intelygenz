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

    def get_edge_test(self):
        redis_client = Mock()
        redis_client.get = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        edge_repo.get_edge("some.edge.id")
        assert redis_client.get.called

    def get_keys_test(self):
        redis_client = Mock()
        redis_client.keys = Mock()
        logger = Mock()
        edge_repo = EdgeRepository(redis_client, logger)
        edge_repo.get_keys()
        assert redis_client.keys.called
