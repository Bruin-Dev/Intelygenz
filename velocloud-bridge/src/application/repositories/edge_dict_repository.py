import json


class EdgeDictRepository:

    def __init__(self, redis_client, logger, keys_prefix):
        self._redis_client = redis_client
        self._logger = logger
        self._keys_prefix = keys_prefix

    def set_serial_to_edge_list(self, serial, edge_ids, time_to_live):
        self._logger.info(f'Saving list of edge_ids')

        redis_key = f'{self._keys_prefix}_{serial}'

        self._redis_client.set(
            redis_key,
            json.dumps(edge_ids, default=str),
            ex=time_to_live,
        )

    def get_serial_to_edge_list(self, serial):
        self._logger.info(f'Getting edge dict from cache')
        redis_key = f'{self._keys_prefix}_{serial}'

        edge_dict = self._redis_client.get(redis_key)
        if edge_dict is not None:
            return json.loads(edge_dict)
        else:
            return None
