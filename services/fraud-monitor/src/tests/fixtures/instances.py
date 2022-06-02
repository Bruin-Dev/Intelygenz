from unittest.mock import Mock

import pytest
from application.actions.fraud_monitoring import FraudMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.utils_repository import UtilsRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asynctest import create_autospec
from config import testconfig
from igz.packages.eventbus.eventbus import EventBus
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger():
    # Let's suppress all logs in tests
    return Mock()


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope="function")
def scheduler():
    return create_autospec(AsyncIOScheduler)


@pytest.fixture(scope="function")
def metrics_repository():
    instance = MetricsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def notifications_repository(logger, event_bus):
    instance = NotificationsRepository(logger=logger, event_bus=event_bus, config=testconfig)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository(event_bus, logger, notifications_repository):
    instance = BruinRepository(
        event_bus=event_bus,
        logger=logger,
        config=testconfig,
        notifications_repository=notifications_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def ticket_repository(utils_repository):
    instance = TicketRepository(utils_repository=utils_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def fraud_monitor(
    event_bus,
    logger,
    scheduler,
    metrics_repository,
    notifications_repository,
    bruin_repository,
    ticket_repository,
    utils_repository,
):
    instance = FraudMonitor(
        event_bus=event_bus,
        logger=logger,
        scheduler=scheduler,
        config=testconfig,
        metrics_repository=metrics_repository,
        notifications_repository=notifications_repository,
        bruin_repository=bruin_repository,
        ticket_repository=ticket_repository,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance
