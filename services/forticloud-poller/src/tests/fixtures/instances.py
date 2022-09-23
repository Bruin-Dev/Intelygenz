from unittest.mock import Mock

import pytest

from application.actions.forticloud_poller import ForticloudPoller
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.redis_repository import RedisRepository
from config import testconfig as config
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def nats_client():
    return Mock()


@pytest.fixture(scope="function")
def redis():
    return Mock()


@pytest.fixture(scope="function")
def scheduler():
    return Mock()


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client, config=config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def redis_repository(redis):
    instance = RedisRepository(
        redis=redis,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def forticloud_poller(nats_client, scheduler, notifications_repository, redis_repository):
    instance = ForticloudPoller(
        nats_client=nats_client,
        scheduler=scheduler,
        config=config,
        redis_repository=redis_repository,
        notifications_repository=notifications_repository,
    )
    wrap_all_methods(instance)

    return instance
