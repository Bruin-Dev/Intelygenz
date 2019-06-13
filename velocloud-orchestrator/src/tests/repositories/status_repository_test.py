from application.repositories.status_repository import StatusRepository
from unittest.mock import Mock


class TestStatusRepository:

    def instance_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        assert isinstance(status_repo, StatusRepository)
        assert status_repo._redis_client is redis_client
        assert status_repo._logger is logger

    def set_status_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        status_repo.set_status("STATUS")
        assert redis_client.set.called
        assert "STATUS" in redis_client.set.call_args[0][1]

    def get_status_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=False)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="IDLE")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_value = status_repo.get_status()
        assert redis_client.exists.called
        assert "status" in redis_client.exists.call_args[0][0]
        assert redis_client.set.called
        assert "status" in redis_client.set.call_args[0][0]
        assert "IDLE" in redis_client.set.call_args[0][1]
        assert "IDLE" in ret_value
        assert redis_client.get.called
        assert "status" in redis_client.get.call_args[0][0]

    def set_edges_to_process_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        edges_2_process = 15
        status_repo.set_edges_to_process(edges_2_process)
        assert redis_client.set.called
        assert "edges_to_process" in redis_client.set.call_args[0][0]
        assert redis_client.set.call_args[0][1] == edges_2_process

    def get_edges_to_process_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=False)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="10")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        status_repo.set_edges_to_process = Mock()
        ret_val = status_repo.get_edges_to_process()
        assert status_repo.set_edges_to_process.called
        assert redis_client.exists.called
        assert "edges_to_process" in redis_client.exists.call_args[0][0]
        assert redis_client.get.called
        assert "edges_to_process" in redis_client.get.call_args[0][0]
        assert ret_val == 10

    def set_edges_processed_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        edges_processed = 15
        status_repo.set_edges_processed(edges_processed)
        assert redis_client.set.called
        assert "edges_processed" in redis_client.set.call_args[0][0]
        assert redis_client.set.call_args[0][1] == edges_processed

    def get_edges_processed_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=False)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="10")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        status_repo.set_edges_processed = Mock()
        ret_val = status_repo.get_edges_processed()
        assert status_repo.set_edges_processed.called
        assert redis_client.exists.called
        assert "edges_processed" in redis_client.exists.call_args[0][0]
        assert redis_client.get.called
        assert "edges_processed" in redis_client.get.call_args[0][0]
        assert ret_val == 10

    def set_last_cycle_timestamp_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        last_cycle_timestamp = 15.120
        status_repo.set_last_cycle_timestamp(last_cycle_timestamp)
        assert redis_client.set.called
        assert "last_cycle_timestamp" in redis_client.set.call_args[0][0]
        assert redis_client.set.call_args[0][1] == last_cycle_timestamp

    def get_last_cycle_timestamp_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=False)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="10.15")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        status_repo.set_last_cycle_timestamp = Mock()
        ret_val = status_repo.get_last_cycle_timestamp()
        assert status_repo.set_last_cycle_timestamp.called
        assert redis_client.exists.called
        assert "last_cycle_timestamp" in redis_client.exists.call_args[0][0]
        assert redis_client.get.called
        assert "last_cycle_timestamp" in redis_client.get.call_args[0][0]
        assert ret_val == 10.15
