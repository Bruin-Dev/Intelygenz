from unittest.mock import Mock

import pytest
from forticloud_client.client import ForticloudClient as ForticloudClientLibrary

from application.actions.refresh_cache import RefreshCache
from application.clients.bruin_client import BruinClient
from application.clients.forticloud_client import ForticloudClient
from application.repositories.bruin_repository import BruinRepository
from application.repositories.cache_repository import CacheRepository
from application.repositories.forticloud_repository import ForticloudRepository
from application.repositories.redis_repository import RedisRepository
from config import testconfig


@pytest.fixture(scope="function")
def redis_client_instance():
    return Mock()


@pytest.fixture(scope="function")
def scheduler_instance():
    return Mock()


@pytest.fixture(scope="function")
def redis_repository_instance(redis_client_instance):
    return RedisRepository(redis_client=redis_client_instance)


@pytest.fixture(scope="function")
def forticloud_client_library_instance():
    return ForticloudClientLibrary(config=testconfig.FORTICLOUD_CONFIG)


@pytest.fixture(scope="function")
def forticloud_instance(forticloud_client_library_instance):
    return ForticloudClient(forticloud_client=forticloud_client_library_instance)


@pytest.fixture(scope="function")
def bruin_client_instance():
    return BruinClient(nats_client=Mock())


@pytest.fixture(scope="function")
def bruin_repository_instance(bruin_client_instance):
    return BruinRepository(bruin_client=bruin_client_instance)


@pytest.fixture(scope="function")
def forticloud_repository_instance(forticloud_instance):
    return ForticloudRepository(forticloud_client=forticloud_instance)


@pytest.fixture(scope="function")
def cache_repository_instance(
    scheduler_instance, redis_repository_instance, forticloud_repository_instance, bruin_repository_instance
):
    return CacheRepository(
        config=testconfig,
        scheduler=scheduler_instance,
        redis_repository=redis_repository_instance,
        forticloud_repository=forticloud_repository_instance,
        bruin_repository=bruin_repository_instance,
    )


@pytest.fixture(scope="function")
def refresh_cache_instance(cache_repository_instance):
    return RefreshCache(cache_repository=cache_repository_instance)
