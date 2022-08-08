from unittest.mock import ANY, Mock

from framework.storage import Utf8Storage
from redis.client import Redis
from tests import given


def data_is_properly_serialized_test():
    storage = any_utf8_storage()
    storage.redis.set = given(ANY, "1234", ex=None).returns(True)

    assert storage.set("any_id", b"\x31\x32\x33\x34")


def data_is_properly_deserialized_test():
    storage = any_utf8_storage()
    storage.redis.get = given(ANY).returns("1234")

    assert storage.find("any_id") == b"\x31\x32\x33\x34"


def any_utf8_storage(
    redis: Redis = Mock(Redis),
    environment: str = "any_environment",
    data_name: str = "any_data_name",
) -> Utf8Storage:
    return Utf8Storage(redis=redis, environment=environment, data_name=data_name)
