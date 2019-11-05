from unittest.mock import Mock
from application.repositories.edge_repository import EdgeRepository


class TestEdgeRepository:

    def instance_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        assert edge_repo._logger is logger

    def set_edge_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        edge_repo.set_edge(123, "some.edge.data")
        assert edge_repo._edge_cache[str(123)] == "some.edge.data"

    def get_edge_ok_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        edge_repo.set_edge(123, "some.edge.data")
        redis_data = edge_repo.get_edge(str(123))
        assert redis_data == "some.edge.data"

    def get_edge_ko_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        redis_data = edge_repo.get_edge("some.edge.id")
        assert redis_data is None

    def set_current_edge_list_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        edge_repo.set_current_edge_list(["some.edge.id", "other.edge.id"])
        assert edge_repo._edge_cache["edge_list"] == ["some.edge.id", "other.edge.id"]

    def get_last_edge_list_ok_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        edge_repo.set_current_edge_list(["some.edge.id", "other.edge.id"])
        redis_data = edge_repo.get_last_edge_list()
        assert redis_data == ["some.edge.id", "other.edge.id"]

    def get_edge_list_ko_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        redis_data = edge_repo.get_last_edge_list()
        assert redis_data is None

    def get_keys_test(self):
        logger = Mock()
        edge_repo = EdgeRepository(logger)
        edge_repo.set_edge(123, "some.edge.data")
        edge_repo.set_current_edge_list(["some.edge.id", "other.edge.id"])
        keys = edge_repo.get_keys()
        assert "123" in keys
        assert "edge_list" in keys
