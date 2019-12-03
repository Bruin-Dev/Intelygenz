from datetime import datetime


class StatusRepository:

    def __init__(self, logger):
        self._status_cache = dict()
        self._logger = logger

    def set_status(self, status):
        self._logger.info(f'Storing status = {status} in cache')
        self._status_cache["status"] = status

    def get_status(self):
        if ("status" in self._status_cache.keys()) is False:
            self._logger.info("Cache has no status' registry. Creating it. State is IDLE")
            self._status_cache["status"] = "IDLE"
        status = self._status_cache["status"]
        self._logger.info(f'Current status from cache: {status}')
        return status

    def set_edges_to_process(self, number_of_edges):
        self._logger.info(f'Storing edges_to_process = {number_of_edges} in cache')
        self._status_cache["edges_to_process"] = number_of_edges

    def get_edges_to_process(self):
        if ("edges_to_process" in self._status_cache.keys()) is False:
            self.set_edges_to_process(0)
        edges_to_process = self._status_cache["edges_to_process"]
        self._logger.info(f'Got edges_to_process = {edges_to_process} from cache')
        return int(edges_to_process)

    def set_edges_processed(self, edges_processed):
        self._logger.info(f'Storing edges_processed = {edges_processed} in cache')
        self._status_cache["edges_processed"] = edges_processed

    def get_edges_processed(self):
        if ("edges_processed" in self._status_cache.keys()) is False:
            self.set_edges_processed(0)
        edges_processed = self._status_cache["edges_processed"]
        self._logger.info(f'Got edges_processed = {edges_processed} from cache')
        return int(edges_processed)

    def set_current_cycle_timestamp(self, current_cycle_timestamp):
        self._logger.info(f'Storing current_cycle_timestamp = {current_cycle_timestamp} in cache')
        self._status_cache["current_cycle_timestamp"] = current_cycle_timestamp

    def get_current_cycle_timestamp(self):
        if ("current_cycle_timestamp" in self._status_cache.keys()) is False:
            self.set_current_cycle_timestamp(datetime.timestamp(datetime(1970, 1, 1)))
        current_cycle_timestamp = self._status_cache["current_cycle_timestamp"]
        self._logger.info(f'Got current_cycle_timestamp = {current_cycle_timestamp} from cache')
        return float(current_cycle_timestamp)

    def set_current_cycle_request_id(self, request_id):
        self._logger.info(f'Storing current_cycle_request_id = {request_id} in cache')
        self._status_cache["current_cycle_request_id"] = request_id

    def get_current_cycle_request_id(self):
        if ("current_cycle_request_id" in self._status_cache.keys()) is False:
            return None
        current_cycle_request_id = self._status_cache["current_cycle_request_id"]
        self._logger.info(f'Got current_cycle_request_id = {current_cycle_request_id} from cache')
        return current_cycle_request_id
