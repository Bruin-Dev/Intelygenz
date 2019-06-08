class StatusRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_status(self, status):
        self._logger(f'Storing status = {status} in cache')
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
        self._logger(f'Storing edges_to_process = {number_of_edges} in cache')
        self._redis_client.set("edges_to_process", number_of_edges)

    def get_edges_to_process(self):
        edges_to_process = self._redis_client.get("edges_to_process")
        self._logger(f'Got edges_to_process = {edges_to_process} from cache')
        return edges_to_process

    def set_edges_processed(self, edges_processed):
        self._logger(f'Storing edges_processed = {edges_processed} in cache')
        self._redis_client.set("edges_processed", edges_processed)

    def get_edges_edges_processed(self):
        edges_processed = self._redis_client.get("edges_processed")
        self._logger(f'Got edges_processed = {edges_processed} from cache')
        return edges_processed
