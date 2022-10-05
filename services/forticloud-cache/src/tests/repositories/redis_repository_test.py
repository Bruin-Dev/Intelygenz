from unittest.mock import Mock

redis_value_example = "[1,2,3,4]"


def get_value_if_exist_return_not_none_test(redis_repository_instance):
    redis_repository_instance.redis_client.exists = Mock(return_value=True)
    redis_repository_instance.redis_client.get = Mock(return_value=redis_value_example)
    redis_values_for_key = redis_repository_instance.get_value_if_exist("some_key")
    assert redis_values_for_key is not None


def get_value_if_exist_return_a_list_test(redis_repository_instance):
    redis_repository_instance.redis_client.exists = Mock(return_value=True)
    redis_repository_instance.redis_client.get = Mock(return_value=redis_value_example)
    redis_values_for_key = redis_repository_instance.get_value_if_exist("some_key")
    assert type(redis_values_for_key) is list


def get_value_if_exist_return_a_list_with_some_value_test(redis_repository_instance):
    redis_repository_instance.redis_client.exists = Mock(return_value=True)
    redis_repository_instance.redis_client.get = Mock(return_value=redis_value_example)
    redis_values_for_key = redis_repository_instance.get_value_if_exist("some_key")
    assert len(redis_values_for_key) > 0


def get_value_if_exist_return_empty_list_when_key_dont_exist_test(redis_repository_instance):
    redis_repository_instance.redis_client.exists = Mock(return_value=False)
    redis_values_for_key = redis_repository_instance.get_value_if_exist("some_key")
    assert len(redis_values_for_key) == 0


def set_value_for_key_return_none_test(redis_repository_instance):
    redis_repository_instance.redis_client.set = Mock()
    redis_values_for_key = redis_repository_instance.set_value_for_key("some_key", "some_value")
    assert redis_values_for_key is None
