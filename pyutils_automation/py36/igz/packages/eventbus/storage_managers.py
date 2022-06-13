import json

from abc import ABC
from abc import abstractmethod
from typing import Union

from shortuuid import uuid


class MessageStorageManager(ABC):  # pragma: no cover
    def __init__(self, logger, storage_client):
        self._logger = logger
        self._storage_client = storage_client

    @staticmethod
    def is_message_larger_than_1mb(msg: Union[str, dict]):
        if isinstance(msg, dict):
            msg = json.dumps(msg, default=str, separators=(',', ':'))

        return len(msg) > 1048576

    @abstractmethod
    def store_message(self, msg: Union[str, dict], encode_result: bool = False) -> Union[str, dict]:
        """ Should receive either an encoded JSON or a dict object. """
        pass

    @abstractmethod
    def recover_message(self, msg: Union[str, dict], encode_result: bool = False) -> Union[str, dict]:
        """ Should receive either an encoded JSON or a dict object. """
        pass


class RedisStorageManager(MessageStorageManager):
    def store_message(self, msg, encode_result=False):
        if isinstance(msg, dict):
            msg = json.dumps(msg, default=str, separators=(',', ':'))

        self._logger.info(f'Storing message within Redis...')

        uuid_ = uuid()
        self._storage_client.set(name=uuid_, value=msg, ex=300)

        self._logger.info(f'Message successfully stored within Redis')

        result = {'token': uuid_, 'is_stored': True}
        if encode_result:
            return json.dumps(result)

        return result

    def recover_message(self, msg, encode_result=False):
        if isinstance(msg, str):
            msg = json.loads(msg)

        self._logger.info(f"Claiming message stored within Redis (payload: {msg})...")

        try:
            token = msg['token']
        except KeyError:
            self._logger.exception(f'Key "token" was not found within the incoming payload {msg}')
            raise
        else:
            stored_msg: str = self._storage_client.get(token)
            self._storage_client.delete(token)

            self._logger.info(f'Message successfully obtained from Redis')

            if encode_result:
                return stored_msg

            return json.loads(stored_msg)
