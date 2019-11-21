import json
import time

from collections import namedtuple
from typing import Dict
from typing import List
from typing import Union


EdgeIdentifier = namedtuple(typename='EdgeIdentifier', field_names=['host', 'enterprise_id', 'edge_id'])


class EdgeRepository:
    def __init__(self, logger, redis_client, keys_prefix):
        self._logger = logger
        self._redis_client = redis_client
        self._keys_prefix = keys_prefix

        self.__edge_key_match_expression = f'{keys_prefix}*'

    def remove_all_stored_elements(self):
        self._logger.info(f'Clearing keys with prefix "{self._keys_prefix}"...')

        keys_to_remove = self._redis_client.scan_iter(match=self.__edge_key_match_expression)
        self._redis_client.delete(*keys_to_remove)

    def add_edge(self, full_id: Union[EdgeIdentifier, dict], status: dict, update_existing=True, time_to_live=60):
        if isinstance(full_id, EdgeIdentifier):
            full_id = dict(full_id._asdict())

        edge_identifier = EdgeIdentifier(**full_id)
        full_id_str = self.__full_id_dict_to_str(full_id)

        if not update_existing and self.exists_edge(full_id):
            self._logger.info(f'Edge {edge_identifier} with {self._keys_prefix} will not be overwritten')
            return

        redis_key = f'{self._keys_prefix}__{full_id_str}'
        value_for_redis_key = {
            'edge_status': status,
            'addition_timestamp': time.time(),
        }
        self._redis_client.set(
            redis_key,
            json.dumps(value_for_redis_key),
            ex=time_to_live,
        )

        self._logger.info(
            f'Edge with {edge_identifier} with prefix {self._keys_prefix} written to Redis successfully'
        )

    def get_edge(self, full_id: Union[EdgeIdentifier, dict]):
        if isinstance(full_id, EdgeIdentifier):
            full_id = dict(full_id._asdict())

        full_id_str = self.__full_id_dict_to_str(full_id)
        redis_key = f'{self._keys_prefix}__{full_id_str}'

        return self._redis_client.get(redis_key)

    def get_all_edges(self) -> Dict[EdgeIdentifier, dict]:
        edges_redis_keys = sorted(list(self._redis_client.scan_iter(match=self.__edge_key_match_expression)))
        values_from_redis = self._redis_client.mget(edges_redis_keys)

        edge_identifiers = (self.__full_id_str_to_edge_identifier(full_id_str) for full_id_str in edges_redis_keys)

        identifier_to_value_pairs = zip(edge_identifiers, values_from_redis)
        return dict(identifier_to_value_pairs)

    def exists_edge(self, full_id: dict):
        full_id_str = self.__full_id_dict_to_str(full_id)
        redis_key = f'{self._keys_prefix}__{full_id_str}'

        return self._redis_client.exists(redis_key)

    def remove_edge(self, full_id: dict):
        edge_identifier = EdgeIdentifier(**full_id)
        full_id_str = self.__full_id_dict_to_str(full_id)
        redis_key = f'{self._keys_prefix}__{full_id_str}'

        self._redis_client.delete(*[redis_key])
        self._logger.info(f'Edge {edge_identifier} with prefix {self._keys_prefix} was removed')

    def __full_id_dict_to_str(self, full_id: dict) -> str:
        edge_host = full_id['host']
        edge_enterprise_id = full_id['enterprise_id']
        edge_id = full_id['edge_id']

        full_id_str = f'{edge_host}|{edge_enterprise_id}|{edge_id}'

        return full_id_str

    def __full_id_str_to_edge_identifier(self, full_id: str) -> dict:
        full_id_components = full_id.split('|')
        full_id_dict = {
            'host': full_id_components[0],
            'enterprise_id': full_id_components[1],
            'edge_id': full_id_components[2],
        }

        return EdgeIdentifier(**full_id_dict)
