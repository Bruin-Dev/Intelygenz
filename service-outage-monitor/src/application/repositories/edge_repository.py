import json


class EdgeRepository:
    def __init__(self, logger, redis_client, root_key):
        self._logger = logger
        self._redis_client = redis_client
        self._root_key = root_key

    def initialize_root_key(self):
        self._logger.info(f'Initializing Redis key "{self._root_key}"...')
        self.reset_root_key()

    def reset_root_key(self):
        self._logger.info(f'Clearing contents for Redis key "{self._root_key}"...')
        self._redis_client.set(self._root_key, {})

    def add_edge(self, full_id, status, update_existing=True):
        full_id_str = self.__compound_full_id_str(full_id)

        if not update_existing and self.exists_edge(full_id):
            self._logger.info(
                f'Edge with full ID "{full_id_str}" will not be overwritten in Redis key "{self._root_key}"'
            )
            return

        stored_edges = self.get_all_edges()
        stored_edges[full_id_str] = status

        self._redis_client.set(self._root_key, json.dumps(stored_edges))
        self._logger.info(
            f'Edge with full ID "{full_id_str}" written in Redis key "{self._root_key}" successfully'
        )

    def get_all_edges(self):
        return json.loads(self._redis_client.get(self._root_key))

    def exists_edge(self, full_id):
        edges = self.get_all_edges()
        full_id_str = self.__compound_full_id_str(full_id)

        return full_id_str in edges.keys()

    def remove_edge(self, full_id):
        edges = self.get_all_edges()

        full_id_str = self.__compound_full_id_str(full_id)
        if full_id_str in edges.keys():
            del edges[full_id_str]
            self._redis_client.set(self._root_key, json.dumps(edges))
            self._logger.info(f'Edge with full ID {full_id_str} removed from Redis key {self._root_key}')

    def __compound_full_id_str(self, full_id_dict):
        edge_host = full_id_dict['host']
        edge_enterprise_id = full_id_dict['enterprise_id']
        edge_id = full_id_dict['edge_id']

        full_id_str = f'{edge_host}|{edge_enterprise_id}|{edge_id}'

        return full_id_str
