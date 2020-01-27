import json


class EdgeDictRepository:

    def __init__(self, redis_client, logger):
        self._redis_client = redis_client
        self._logger = logger

    def set_current_edge_dict(self, edge_dict):
        self._logger.info(f'Saving edge dict with data:  {edge_dict}')
        self._redis_client.set(
            "edge_dict",
            json.dumps(edge_dict, default=str)
        )

    def get_last_edge_dict(self):
        self._logger.info(f'Getting edge dict from cache')
        edge_dict = self._redis_client.get("edge_dict")
        self._logger.info(f'edge_dict = {edge_dict}')
        if edge_dict is not None:
            return json.loads(edge_dict)
        else:
            return None
