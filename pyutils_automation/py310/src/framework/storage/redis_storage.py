import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Iterator, Optional, Type, TypeVar

from redis.client import Redis

T = TypeVar("T")

log = logging.getLogger(__name__)


@dataclass
class RedisStorage(Generic[T], ABC):
    """
    Redis wrapper that manages generic T type record keys and storage operations.
    """

    redis: Redis
    environment: str
    data_name: str
    data_type: Type[T]

    def __post_init__(self):
        log.info(
            "Initialized RedisStorage("
            f"redis={self.redis}, "
            f"environment={self.environment}, "
            f"data_name={self.data_name}, "
            f"data_type={self.data_type})"
        )

    def exists(self, *ids: str) -> int:
        """
        Checks if any records are currently stored.
        :param ids: the record IDs to be checked
        :return: the number of existing records found
        """
        log.debug(f"exists(ids={ids})")
        keys = [self._key(id) for id in ids]
        existing_records = self.redis.exists(*keys)
        log.debug(f"redis.exists({keys})={existing_records}")

        return existing_records

    def find(self, id: str) -> Optional[T]:
        """
        Find a record given its ID.
        :param id: a record ID
        :return: the record if it was found, None otherwise
        """
        log.debug(f"get(id={id})")
        key = self._key(id)
        return self._get(key)

    def find_all(self) -> Iterator[T]:
        """
        :return: all existing data_name records
        """
        log.debug(f"find_all()")
        pattern = self._key("*")
        return [self._get(key) for key in self.redis.scan_iter(pattern)]

    def set(self, id: str, data: T, ttl_seconds: Optional[int] = None) -> bool:
        """
        Stores a record.
        :param id: a record ID
        :param data: the record data
        :param ttl_seconds: record time to live in secods
        :return: True if the record was successfully stored, False otherwise
        """
        log.debug(f"set(id={id}, data={data}, ttl_seconds={ttl_seconds})")
        key = self._key(id)
        result = self.redis.set(key, self._serialize(data), ex=ttl_seconds)
        log.debug(f"redis.set({key}, ****, ex={ttl_seconds})={result}")

        return bool(result)

    def delete(self, *ids: str) -> int:
        """
        Removes several records given its ids.
        :param ids: ids of the records to be removed
        :return: the number of records that were removed
        """
        log.debug(f"delete(ids={ids})")
        keys = [self._key(key) for key in ids]
        deleted_records = self.redis.delete(*keys)
        log.debug(f"redis.delete({keys})={deleted_records}")

        return deleted_records

    def _get(self, key: str) -> Optional[T]:
        """
        Internal method to get a record given its key.
        The record data will get deserialized.
        :param key: a key record
        :return: a record
        """
        log.debug(f"_get(key={key})")
        raw_data = self.redis.get(key)
        log.debug(f"redis.get()={raw_data}")
        return self._deserialize(raw_data)

    def _key(self, id: str) -> str:
        """
        Internal method to build the key of a record given its ID.
        :param id: id of the record
        :return: key of the record
        """
        log.debug(f"key(id={id})")
        return f"{self.environment}:{self.data_name}:{id}"

    @abstractmethod
    def _serialize(self, data: T) -> str:
        """
        Serializes a storage data_type to str.
        :param data: data to be serialized
        :return: serialized str
        """

    @abstractmethod
    def _deserialize(self, data: Optional[str]) -> Optional[T]:
        """
        Deserializes a str to the storage data_type.
        :param data: str to be deserialized
        :return: deserialized data_type
        """
