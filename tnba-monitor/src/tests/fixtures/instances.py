from unittest.mock import Mock

import pytest

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asynctest import create_autospec

from igz.packages.eventbus.eventbus import EventBus

from application.actions.tnba_monitor import TNBAMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.prediction_repository import PredictionRepository
from application.repositories.t7_repository import T7Repository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig as config
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope='function')
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
    instance = NotificationsRepository(event_bus=event_bus, config=config)
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
def velocloud_repository(logger, event_bus, notifications_repository):
    instance = VelocloudRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def t7_repository(logger, event_bus, notifications_repository):
    instance = T7Repository(
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
def prediction_repository(utils_repository):
    instance = PredictionRepository(
        utils_repository=utils_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def ticket_repository(utils_repository):
    instance = TicketRepository(
        utils_repository=utils_repository,
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
def tnba_monitor(event_bus, logger, scheduler, t7_repository, bruin_repository, velocloud_repository,
                 customer_cache_repository, notifications_repository, prediction_repository, ticket_repository,
                 utils_repository):
    instance = TNBAMonitor(
        event_bus=event_bus,
        logger=logger,
        scheduler=scheduler,
        config=config,
        bruin_repository=bruin_repository,
        velocloud_repository=velocloud_repository,
        t7_repository=t7_repository,
        customer_cache_repository=customer_cache_repository,
        notifications_repository=notifications_repository,
        prediction_repository=prediction_repository,
        ticket_repository=ticket_repository,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance
