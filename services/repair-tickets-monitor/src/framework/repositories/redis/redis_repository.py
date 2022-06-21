from typing import Generic, Iterator, Optional, Type, TypeVar

from dataclasses import dataclass
from pydantic import BaseModel
from redis.client import Redis

T = TypeVar("T", bound=BaseModel)


@dataclass
class RedisRepository(Generic[T]):
    redis: Redis
    environment: str
    entity_name: str
    entity_type: Type[T]

    def _get(self, key: str) -> T:
        return self.entity_type.parse_raw(self.redis.get(key))

    def key(self, id: str) -> str:
        return f"{self.environment}:{self.entity_name}:{id}"

    def exists(self, id: str) -> bool:
        return bool(self.redis.exists(self.key(id)))

    def find(self, id: str) -> Optional[T]:
        key = self.key(id)
        if self.exists(key):
            return self._get(key)
        else:
            return None

    def find_all(self) -> Iterator[T]:
        pattern = self.key("*")
        return [self._get(key) for key in self.redis.scan_iter(pattern)]

    def store(self, id: str, data: T) -> bool:
        key = self.key(id)
        return self.redis.set(key, data.json())

    def remove(self, *ids) -> bool:
        keys = [self.key(key) for key in ids]
        return bool(self.redis.delete(*keys))
