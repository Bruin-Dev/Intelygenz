from application.repositories.status_repository import StatusRepository
from unittest.mock import Mock
from datetime import datetime


class TestStatusRepository:

    def instance_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        assert status_repo._logger is logger

    def set_status_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        status_repo.set_status("STATUS")
        assert status_repo._status_cache["status"] == "STATUS"

    def get_status_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        ret_value = status_repo.get_status()
        assert ret_value == "IDLE"
        status_repo.set_status("OK")
        ret_value2 = status_repo.get_status()
        assert ret_value2 == "OK"

    def set_edges_to_process_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        edges_2_process = 15
        status_repo.set_edges_to_process(edges_2_process)
        assert status_repo._status_cache["edges_to_process"] == edges_2_process

    def get_edges_to_process_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        ret_val = status_repo.get_edges_to_process()
        assert ret_val == 0
        status_repo.set_edges_to_process(15)
        ret_val2 = status_repo.get_edges_to_process()
        assert ret_val2 == 15

    def set_edges_processed_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        edges_processed = 15
        status_repo.set_edges_processed(edges_processed)
        assert status_repo._status_cache["edges_processed"] == 15

    def get_edges_processed_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        ret_val = status_repo.get_edges_processed()
        assert ret_val == 0
        status_repo.set_edges_processed(15)
        ret_val2 = status_repo.get_edges_processed()
        assert ret_val2 == 15

    def set_current_cycle_timestamp_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        current_cycle_timestamp = 15.120
        status_repo.set_current_cycle_timestamp(current_cycle_timestamp)
        assert status_repo._status_cache["current_cycle_timestamp"] == current_cycle_timestamp

    def get_current_cycle_timestamp_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        ret_val = status_repo.get_current_cycle_timestamp()
        assert ret_val == datetime.timestamp(datetime(1970, 1, 1))
        status_repo.set_current_cycle_timestamp(15.120)
        ret_val2 = status_repo.get_current_cycle_timestamp()
        assert ret_val2 == 15.120

    def set_current_cycle_request_id_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        current_cycle_request_id = 15
        status_repo.set_current_cycle_request_id(current_cycle_request_id)
        assert status_repo._status_cache["current_cycle_request_id"] == 15

    def get_current_cycle_request_id_OK_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        status_repo.set_current_cycle_request_id('10')
        ret_val = status_repo.get_current_cycle_request_id()
        assert ret_val == '10'

    def get_current_cycle_request_id_KO_test(self):
        logger = Mock()
        status_repo = StatusRepository(logger)
        ret_val = status_repo.get_current_cycle_request_id()
        assert ret_val is None
