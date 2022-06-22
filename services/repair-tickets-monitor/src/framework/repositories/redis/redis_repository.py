import logging
from typing import Generic, Iterator, Optional, Type, TypeVar

from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from redis.client import Redis

T = TypeVar("T", bound=BaseModel)

log = logging.getLogger(__name__)


@dataclass
class RedisRepository(Generic[T]):
    """
    Redis wrapper that manages storage operations on a generic T model.
    The model must be a pydantic's BaseModel subclass for the wrapper
    uses pydantic's .json() serialization and .parse_raw() deserialization
    methods.
    """

    redis: Redis
    environment: str
    model_name: str
    model_type: Type[T]

    def key(self, id: str) -> str:
        """
        Build the key of a model record given its ID

        :param id: id of the model record
        :return: key of the model record
        """
        return f"{self.environment}:{self.model_name}:{id}"

    def exists(self, id: str) -> bool:
        """
        Checks if a given model record exists
        :param id: a model record ID
        :return: True if it exists, False otherwise
        """
        return self.redis.exists(self.key(id)) == 1

    def find(self, id: str) -> Optional[T]:
        """
        Find a model record given its ID
        :param id: a model record ID
        :return: the model record if it was found, None otherwise
        """
        key = self.key(id)
        if self.exists(key):
            return self._get(key)
        else:
            return None

    def find_all(self) -> Iterator[T]:
        """
        :return: All existing model records
        """
        pattern = self.key("*")
        return [self._get(key) for key in self.redis.scan_iter(pattern)]

    def store(self, id: str, data: T, stl: Optional[int] = None) -> bool:
        """
        Stores a model record
        :param id: a model record ID
        :param data: a model record
        :param stl: seconds to live if needed
        :return: True if the model record was successfully stored, False otherwise
        """
        key = self.key(id)
        return self.redis.set(key, data.json(), ex=stl)

    def delete(self, *ids) -> bool:
        """
        Removes one or several model records
        :param ids: ids of the model records to be removed
        :return: Ture if the model records were successfully removed, False otherwise
        """
        keys = [self.key(key) for key in ids]
        return self.redis.delete(*keys) == 1

    def _get(self, key: str) -> Optional[T]:
        """
        Shorthand method to deserialize a model record given its key.
        It assumes that the model record exists and that its data can be deserialized into the generic model T.
        :param key: key of a model record
        :return: a model record
        """
        try:
            return self.model_type.parse_raw(self.redis.get(key))
        except ValidationError as e:
            log.warning(f"Redis model {key} coulnd't be deserialized: {e}")
            return None
