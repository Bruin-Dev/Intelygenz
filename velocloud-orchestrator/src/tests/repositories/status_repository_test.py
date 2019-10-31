from application.repositories.status_repository import StatusRepository
from unittest.mock import Mock


class TestStatusRepository:

    def instance_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        assert status_repo._logger is logger

    def set_status_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        status_repo.set_status("STATUS")
        assert status_repo._status_cache["status"] == "STATUS"

    def get_status_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_value = status_repo.get_status()
        assert ret_value == "IDLE"

    def set_edges_to_process_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        edges_2_process = 15
        status_repo.set_edges_to_process(edges_2_process)
        assert status_repo._status_cache["edges_to_process"] == edges_2_process

    def get_edges_to_process_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_val = status_repo.get_edges_to_process()
        assert ret_val == 0

    def set_edges_processed_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        edges_processed = 15
        status_repo.set_edges_processed(edges_processed)
        assert status_repo._status_cache["edges_processed"] == 15

    def get_edges_processed_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_val = status_repo.get_edges_processed()
        assert ret_val == 0

    def set_current_cycle_timestamp_test(self):
        redis_client = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        current_cycle_timestamp = 15.120
        status_repo.set_current_cycle_timestamp(current_cycle_timestamp)
        assert status_repo._status_cache["current_cycle_timestamp"] == current_cycle_timestamp

    def get_current_cycle_timestamp_test(self):
        redis_client = Mock()
        logger = Mock()
        ret_val = status_repo.get_current_cycle_timestamp()
        assert status_repo.set_current_cycle_timestamp.called
        assert redis_client.exists.called
        assert "current_cycle_timestamp" in redis_client.exists.call_args[0][0]
        assert redis_client.get.called
        assert "current_cycle_timestamp" in redis_client.get.call_args[0][0]
        assert ret_val == 10.15

    def set_current_cycle_request_id_test(self):
        redis_client = Mock()
        redis_client.set = Mock()
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        current_cycle_request_id = 15
        status_repo.set_current_cycle_request_id(current_cycle_request_id)
        assert redis_client.set.called
        assert "current_cycle_request_id" in redis_client.set.call_args[0][0]
        assert redis_client.set.call_args[0][1] == current_cycle_request_id

    def get_current_cycle_request_id_OK_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=True)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="10")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_val = status_repo.get_current_cycle_request_id()
        assert redis_client.exists.called
        assert "current_cycle_request_id" in redis_client.exists.call_args[0][0]
        assert redis_client.get.called
        assert "current_cycle_request_id" in redis_client.get.call_args[0][0]
        assert ret_val == '10'

    def get_current_cycle_request_id_KO_test(self):
        redis_client = Mock()
        redis_client.exists = Mock(return_value=False)
        redis_client.set = Mock()
        redis_client.get = Mock(return_value="10")
        logger = Mock()
        status_repo = StatusRepository(redis_client, logger)
        ret_val = status_repo.get_current_cycle_request_id()
        assert redis_client.exists.called
        assert redis_client.get.called is False
        assert ret_val is None
