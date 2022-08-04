from unittest.mock import ANY, Mock

from pydantic import BaseModel
from redis.client import Redis

from framework.storage.model import ModelStorage
from framework.testing import given


def models_are_properly_serialized_test():
    storage = any_model_storage()
    storage.redis.set = given(ANY, '{"field": "value"}', ex=None).returns(True)

    assert storage.set("any_id", AnyModel(field="value"))


def models_are_properly_deserialized_test():
    storage = any_model_storage()
    storage.redis.get = given(ANY).returns('{"field": "value"}')

    assert storage.find("any_id") == AnyModel(field="value")


def non_deserializable_values_are_properly_handled_test():
    storage = any_model_storage()
    storage.redis.get = given(ANY).returns("non_deserializable")

    assert storage.find("any_id") is None


class AnyModel(BaseModel):
    field: str = "value"


def any_model_storage(
    redis: Redis = Mock(Redis),
    environment: str = "any_environment",
    data_name: str = "any_data_name",
) -> ModelStorage[AnyModel]:
    return ModelStorage(redis=redis, environment=environment, data_name=data_name, data_type=AnyModel)
