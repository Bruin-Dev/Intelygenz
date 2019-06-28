class EdgeRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_edge(self, edge_id, edge_status):
        self._logger.info(f'Saving edge with data: edge_id = {edge_id}, edge_status = {edge_status}')
        self._redis_client.set(str(edge_id), edge_status)

    def get_edge(self, edge_id):
        self._logger.info(f'Getting data for edge_id = {edge_id}...')
        edge_data = self._redis_client.get(edge_id)
        self._logger.info(f'edge_data = {edge_data}')
        return edge_data

    def get_keys(self):
        self._logger.info(f'Getting keys from redis')
        redis_keys = self._redis_client.keys()
        return redis_keys
