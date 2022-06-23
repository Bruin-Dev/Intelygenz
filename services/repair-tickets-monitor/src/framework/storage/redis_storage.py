import logging
from abc import ABC, abstractmethod
from typing import Generic, Iterator, Optional, Type, TypeVar

from dataclasses import dataclass
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

    def exists(self, id: str) -> bool:
        """
        Checks if a given record exists
        :param id: a record ID
        :return: True if it exists, False otherwise
        """
        log.debug(f"exists(id={id})")
        redis_signal = self.redis.exists(self._key(id))
        log.debug(f"exists(): redis.exists()={redis_signal}")

        return redis_signal == 1

    def find(self, id: str) -> Optional[T]:
        """
        Find a record given its ID
        :param id: a record ID
        :return: the record if it was found, None otherwise
        """
        log.debug(f"get(id={id})")
        key = self._key(id)
        return self._get(key)

    def find_all(self) -> Iterator[T]:
        """
        :return: All existing records
        """
        log.debug(f"find_all()")
        pattern = self._key("*")
        return [self._get(key) for key in self.redis.scan_iter(pattern)]

    def set(self, id: str, data: T, stl: Optional[int] = None) -> bool:
        """
        Stores a record
        :param id: a record ID
        :param data: the record data
        :param stl: seconds to live if needed
        :return: True if the record was successfully stored, False otherwise
        """
        log.debug(f"set(id={id}, data={data}, stl={stl})")
        key = self._key(id)
        result = self.redis.set(key, self._serialize(data), ex=stl)
        log.debug(f"set(): redis.set()={result}")

        return result

    def delete(self, *ids) -> bool:
        """
        Removes several records given its ids
        :param ids: ids of the records to be removed
        :return: Ture if the records were successfully removed, False otherwise
        """
        log.debug(f"delete(ids={ids})")
        keys = [self._key(key) for key in ids]
        redis_signal = self.redis.delete(*keys)
        log.debug(f"delete(): redis.delete()={redis_signal}")

        return redis_signal == 1

    def _get(self, key: str) -> Optional[T]:
        """
        Internal method to get a record given its key.
        The record data will get deserialized
        :param key: a key record
        :return:
        """
        log.debug(f"_get(key={key})")
        raw_data = self.redis.get(key)
        log.debug(f"_get(): redis.get()={raw_data}")
        return self._deserialize(raw_data)

    def _key(self, id: str) -> str:
        """
        Internal method to build the key of a record given its ID
        :param id: id of the record
        :return: key of the record
        """
        log.debug(f"key(id={id})")
        return f"{self.environment}:{self.data_name}:{id}"

    @abstractmethod
    def _serialize(self, data: T) -> str:
        """
        Serializes a storage data_type to str
        :param data: data to be serialized
        :return: serialized str
        """
        pass

    @abstractmethod
    def _deserialize(self, data: Optional[str]) -> Optional[T]:
        """
        Deserializes a str to the storage data_type
        :param data: str to be deserialized
        :return: deserialized data_type
        """
        pass
