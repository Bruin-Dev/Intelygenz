from unittest.mock import Mock

import pytest
from application.actions.affecting_monitoring import AffectingMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import testconfig as config
from framework.nats.client import Client as NatsClient
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def nats_client():
    return Mock(spec_set=NatsClient)


@pytest.fixture(scope="function")
def scheduler():
    return Mock(spec_set=AsyncIOScheduler)


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository(nats_client, notifications_repository):
    instance = BruinRepository(
        nats_client=nats_client,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def hawkeye_repository(nats_client, notifications_repository):
    instance = HawkeyeRepository(
        nats_client=nats_client,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def customer_cache_repository(nats_client, notifications_repository):
    instance = CustomerCacheRepository(
        nats_client=nats_client,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def affecting_monitor(
    scheduler,
    bruin_repository,
    hawkeye_repository,
    customer_cache_repository,
    notifications_repository,
    utils_repository,
):
    instance = AffectingMonitor(
        scheduler=scheduler,
        config=config,
        bruin_repository=bruin_repository,
        hawkeye_repository=hawkeye_repository,
        customer_cache_repository=customer_cache_repository,
        notifications_repository=notifications_repository,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance
