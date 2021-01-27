from unittest.mock import Mock

import pytest

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asynctest import create_autospec

from igz.packages.eventbus.eventbus import EventBus

from application.actions.affecting_monitoring import AffectingMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from config import testconfig as config
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope='session')
def logger():
    # Let's suppress all logs in tests
    return Mock()


@pytest.fixture(scope='function')
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope='function')
def scheduler():
    return create_autospec(AsyncIOScheduler)


@pytest.fixture(scope='function')
def notifications_repository(event_bus):
    instance = NotificationsRepository(event_bus=event_bus)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def bruin_repository(logger, event_bus, notifications_repository):
    instance = BruinRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def hawkeye_repository(logger, event_bus, notifications_repository):
    instance = HawkeyeRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def customer_cache_repository(logger, event_bus, notifications_repository):
    instance = CustomerCacheRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def affecting_monitor(logger, scheduler, bruin_repository, hawkeye_repository, customer_cache_repository,
                      notifications_repository, utils_repository):
    instance = AffectingMonitor(
        logger=logger,
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
