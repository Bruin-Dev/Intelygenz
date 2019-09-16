class EdgeRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_edge(self, edge_id, edge_status):
        self._logger.info(f'Saving edge with data: edge_id = {edge_id}, edge_status = {edge_status}')
        self._redis_client.set(str(edge_id), edge_status)

    def get_edge(self, edge_id):
        if self._redis_client.exists(edge_id):
            self._logger.info(f'Getting data for edge_id = {edge_id}...')
            edge_data = self._redis_client.get(edge_id)
            self._logger.info(f'edge_data = {edge_data}')
            return edge_data

    def set_current_edge_list(self, edge_list):
        self._logger.info(f'Saving edge list with data:  {edge_list}')
        self._redis_client.set("edge_list", edge_list)

    def get_last_edge_list(self):
        if self._redis_client.exists("edge_list"):
            self._logger.info(f'Getting edge list from redis')
            edge_list = self._redis_client.get("edge_list")
            self._logger.info(f'edge_list = {edge_list}')
            return edge_list

    def get_keys(self):
        self._logger.info(f'Getting keys from redis')
        redis_keys = self._redis_client.keys()
        return redis_keys
