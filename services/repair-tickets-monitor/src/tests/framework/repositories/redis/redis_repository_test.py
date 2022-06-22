from unittest.mock import ANY, Mock

from framework.repositories.redis.redis_repository import RedisRepository
from pydantic import BaseModel
from redis.client import Redis
from tests import case, given


def keys_are_properly_built_test():
    repository = any_redis_repository(environment="any_environment", model_name="any_model_name")
    assert repository.key("any_id") == "any_environment:any_model_name:any_id"


def existing_keys_are_properly_found_test():
    repository = any_redis_repository()
    repository.redis.exists = given(ANY).returns(1)

    assert repository.exists("any_id")


def existing_models_are_properly_found_test():
    model = any_model()
    repository = any_redis_repository()
    repository.redis.exists = given(ANY).returns(1)
    repository.redis.get = given(ANY).returns(model.json())

    assert repository.find("any_id") == model


def missing_models_are_properly_returned_test():
    repository = any_redis_repository()
    repository.redis.exists = given(ANY).returns(0)

    assert repository.find("any_id") is None


def conflicting_models_are_properly_returned_test():
    repository = any_redis_repository()
    repository.redis.exists = given(ANY).returns(1)
    repository.redis.get = given(ANY).returns(None)

    assert repository.find("any_id") is None


def badly_serialized_models_are_properly_returned_test():
    repository = any_redis_repository()
    repository.redis.exists = given(ANY).returns(1)
    repository.redis.get = given(ANY).returns("badly_serialized_model")

    assert repository.find("any_id") is None


def all_existing_models_are_properly_found_test():
    model_1 = any_model(field="field_1")
    model_2 = any_model(field="field_2")
    models = {"model_1": model_1, "model_2": model_2}
    repository = any_redis_repository(environment="any_environment", model_name="any_model_name")
    repository.redis.scan_iter = given("any_environment:any_model_name:*").returns(models.keys())
    repository.redis.get = case(
        given("model_1").returns(model_1.json()),
        given("model_2").returns(model_2.json()),
    )

    assert repository.find_all() == [model_1, model_2]


def models_are_properly_stored_test():
    model = any_model()
    repository = any_redis_repository(environment="any_environment", model_name="any_model_name")
    repository.redis.set = given("any_environment:any_model_name:any_id", model.json(), ex=None).returns(True)

    assert repository.store("any_id", model)


def models_are_properly_stored_with_stl_test():
    stl = hash("any_stl")
    repository = any_redis_repository()
    repository.redis.set = given(ANY, ANY, ex=stl).returns(1)

    assert repository.store("any_id", any_model(), stl=stl)


def models_are_properly_deleted_test():
    repository = any_redis_repository()
    repository.redis.delete = given(ANY).returns(1)

    assert repository.delete("any_id")


class AnyModel(BaseModel):
    field: str


def any_model(field: str = "any_value"):
    return AnyModel(field=field)


def any_redis_repository(
    redis: Redis = Mock(Redis),
    environment: str = "any_environment",
    model_name: str = "any_model_name",
) -> RedisRepository[AnyModel]:
    return RedisRepository[AnyModel](
        redis=redis,
        environment=environment,
        model_name=model_name,
        model_type=AnyModel,
    )
