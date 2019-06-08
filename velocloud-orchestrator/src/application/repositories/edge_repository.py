from datetime import datetime


class EdgeRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_edge(self, edge_id, edge_status):
        self._logger.info(f'Saving edge with data: edge_id = {edge_id}, edge_status = {edge_status}')
        self._redis_client.hset(edge_id, "edge_status", edge_status, "last_processed", repr(datetime.now()))

    def get_edge(self, edge_id):
        self._logger.info(f'Getting data for edge_id = {edge_id}...')
        edge_data = self._redis_client.hgetall(edge_id)
        self._logger.info(f'edge_data = {edge_data}')
        return edge_data
