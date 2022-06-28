from typing import Optional, Type
from unittest.mock import ANY, Mock

from dataclasses import dataclass
from framework.storage.redis_storage import RedisStorage
from pydantic import BaseModel
from redis.client import Redis
from tests import case, given


def existing_keys_are_properly_found_test():
    storage = any_redis_storage()
    storage.redis.exists = given(ANY).returns(1)

    assert storage.exists("any_id") == 1


def multiple_existing_keys_are_properly_found_test():
    storage = any_redis_storage()
    storage.redis.exists = given(ANY, ANY).returns(2)

    assert storage.exists("any_id", "any_other_id")


def existing_records_are_properly_found_test():
    data = "any_data"
    storage = any_redis_storage()
    storage.redis.get = given(ANY).returns(data)

    assert storage.find("any_id") == data


def missing_records_are_properly_returned_test():
    storage = any_redis_storage()
    storage.redis.get = given(ANY).returns(None)

    assert storage.find("any_id") is None


def all_existing_records_are_properly_found_test():
    data_1 = "any_data_1"
    data_2 = "any_data_2"
    models = {"data_1": data_1, "data_2": data_2}
    storage = any_redis_storage()
    storage.redis.scan_iter = given(ANY).returns(models.keys())
    storage.redis.get = case(
        given("data_1").returns(data_1),
        given("data_2").returns(data_2),
    )

    assert storage.find_all() == [data_1, data_2]


def records_are_properly_stored_test():
    data = "any_data"
    storage = any_redis_storage()
    storage.redis.set = given(ANY, data, ex=None).returns(True)

    assert storage.set("any_id", data)


def records_are_properly_stored_with_ttl_test():
    ttl_seconds = hash("any_ttl_seconds")
    storage = any_redis_storage()
    storage.redis.set = given(ANY, ANY, ex=ttl_seconds).returns(1)

    assert storage.set("any_id", "any_data", ttl_seconds=ttl_seconds)


def records_are_properly_deleted_test():
    storage = any_redis_storage()
    storage.redis.delete = given(ANY).returns(1)

    assert storage.delete("any_id") == 1


def multiple_records_are_properly_deleted_test():
    storage = any_redis_storage()
    storage.redis.delete = given(ANY, ANY).returns(2)

    assert storage.delete("any_id", "any_other_id") == 2


class AnyModel(BaseModel):
    field: str


def any_model(field: str = "any_value"):
    return AnyModel(field=field)


@dataclass
class AnyRedisStorage(RedisStorage[str]):
    data_type: Type = str

    def _serialize(self, data: str) -> str:
        return data

    def _deserialize(self, data: Optional[str]) -> Optional[str]:
        return data


def any_redis_storage(
    redis: Redis = Mock(Redis),
    environment: str = "any_environment",
    data_name: str = "any_data_name",
) -> AnyRedisStorage:
    return AnyRedisStorage(redis=redis, environment=environment, data_name=data_name)
