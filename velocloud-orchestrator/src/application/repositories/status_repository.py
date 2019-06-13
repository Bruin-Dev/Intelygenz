from datetime import datetime


class StatusRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_status(self, status):
        self._logger.info(f'Storing status = {status} in cache')
        self._redis_client.set("status", status)

    def get_status(self):
        if not self._redis_client.exists("status"):
            self._logger.info("Cache has no status' registry. Creating it. State is IDLE")
            self._redis_client.set("status", "IDLE")
            return "IDLE"
        status = self._redis_client.get("status")
        self._logger.info(f'Current status from cache: {status}')
        return status

    def set_edges_to_process(self, number_of_edges):
        self._logger.info(f'Storing edges_to_process = {number_of_edges} in cache')
        self._redis_client.set("edges_to_process", number_of_edges)

    def get_edges_to_process(self):
        if not self._redis_client.exists("edges_to_process") or self._redis_client.get("edges_to_process") is None:
            self.set_edges_to_process(0)
        edges_to_process = self._redis_client.get("edges_to_process")
        self._logger.info(f'Got edges_to_process = {edges_to_process} from cache')
        return int(edges_to_process)

    def set_edges_processed(self, edges_processed):
        self._logger.info(f'Storing edges_processed = {edges_processed} in cache')
        self._redis_client.set("edges_processed", edges_processed)

    def get_edges_processed(self):
        if not self._redis_client.exists("edges_processed") or self._redis_client.get("edges_processed") is None:
            self.set_edges_processed(0)
        edges_processed = self._redis_client.get("edges_processed")
        self._logger.info(f'Got edges_processed = {edges_processed} from cache')
        return int(edges_processed)

    def set_last_cycle_timestamp(self, last_cycle_timestamp):
        self._logger.info(f'Storing last_cycle_timestamp = {last_cycle_timestamp} in cache')
        self._redis_client.set("last_cycle_timestamp", last_cycle_timestamp)

    def get_last_cycle_timestamp(self):
        if not self._redis_client.exists("last_cycle_timestamp") or self._redis_client.get(
                "last_cycle_timestamp") is None:
            self.set_edges_processed(datetime.timestamp(datetime(1970, 1, 1)))
        last_cycle_timestamp = self._redis_client.get("last_cycle_timestamp")
        self._logger.info(f'Got last_cycle_timestamp = {last_cycle_timestamp} from cache')
        return float(last_cycle_timestamp)
