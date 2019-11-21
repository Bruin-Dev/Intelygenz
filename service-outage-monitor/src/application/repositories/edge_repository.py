import json
import time

from collections import namedtuple
from typing import Dict
from typing import List
from typing import Union


EdgeIdentifier = namedtuple(typename='EdgeIdentifier', field_names=['host', 'enterprise_id', 'edge_id'])


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

    def add_edge(self, full_id: Union[EdgeIdentifier, dict], status: dict, update_existing=True, time_to_live=60):
        stored_edges = self._get_all_edges_raw()
        self.__add_edge_to_store(stored_edges, full_id, status, update_existing=update_existing)
        self._redis_client.set(self._root_key, json.dumps(stored_edges), ex=time_to_live)

    def add_edge_set(self, new_edges: Dict[EdgeIdentifier, dict], update_existing=True, time_to_live=60):
        # TODO: Add support for full IDs with dict format (not only EdgeIdentifier format)
        stored_edges = self._get_all_edges_raw()

        for full_id, edge_value in new_edges.items():
            self.__add_edge_to_store(stored_edges, full_id, edge_value, update_existing=update_existing)

        self._redis_client.set(self._root_key, json.dumps(stored_edges), ex=time_to_live)

    def get_edge(self, full_id: Union[EdgeIdentifier, dict]):
        if isinstance(full_id, EdgeIdentifier):
            full_id = dict(full_id._asdict())

        edges = self._get_all_edges_raw()
        full_id_str = self.__full_id_dict_to_str(full_id)

        return edges.get(full_id_str)

    def get_all_edges(self) -> Dict[EdgeIdentifier, dict]:
        edges_from_redis = self._get_all_edges_raw()
        return {
            self.__full_id_str_to_edge_identifier(full_id_str): value
            for full_id_str, value in edges_from_redis.items()
        }

    def exists_edge(self, full_id: dict):
        edges = self._get_all_edges_raw()
        full_id_str = self.__full_id_dict_to_str(full_id)

        return full_id_str in edges.keys()

    def remove_edge(self, full_id: dict):
        stored_edges = self._get_all_edges_raw()

        self.__remove_edge_from_store(stored_edges, full_id)
        self._redis_client.set(self._root_key, json.dumps(stored_edges))

    def remove_edge_set(self, *edges_to_remove):
        stored_edges = self._get_all_edges_raw()

        for full_id in edges_to_remove:
            self.__remove_edge_from_store(stored_edges, full_id)

        self._redis_client.set(self._root_key, json.dumps(stored_edges))

    def _get_all_edges_raw(self) -> Dict[str, dict]:
        return json.loads(self._redis_client.get(self._root_key))

    def __add_edge_to_store(self, stored_edges: Dict[str, dict], full_id: Union[EdgeIdentifier, dict], status: dict,
                            **kwargs):
        if isinstance(full_id, EdgeIdentifier):
            full_id = dict(full_id._asdict())

        edge_identifier = EdgeIdentifier(**full_id)
        full_id_str = self.__full_id_dict_to_str(full_id)

        if not kwargs.get('update_existing', True) and self.exists_edge(full_id):
            self._logger.info(
                f'Edge with {edge_identifier} will not be overwritten in Redis key "{self._root_key}"'
            )
            return

        stored_edges[full_id_str] = {
            'edge_status': status,
            'addition_timestamp': time.time(),
        }
        self._logger.info(
            f'Edge with {edge_identifier} written in Redis key "{self._root_key}" successfully'
        )

    def __remove_edge_from_store(self, stored_edges: Dict[str, dict], full_id: dict):
        edge_identifier = EdgeIdentifier(**full_id)
        full_id_str = self.__full_id_dict_to_str(full_id)

        if full_id_str in stored_edges.keys():
            del stored_edges[full_id_str]
            self._logger.info(f'Edge with {edge_identifier} removed from Redis key {self._root_key}')

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
