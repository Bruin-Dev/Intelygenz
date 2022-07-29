from unittest.mock import Mock

import pytest
from application.actions.intermapper_monitoring import InterMapperMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.dri_repository import DRIRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asynctest import create_autospec
from config import testconfig as config
from igz.packages.eventbus.eventbus import EventBus
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger():
    # Let's suppress all logs in tests
    return Mock()


@pytest.fixture(scope="function")
def metrics_repository():
    # Let's fake this repository so we don't depend on a metrics server to write stuff for Prometheus
    return Mock()


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope="function")
def scheduler():
    return create_autospec(AsyncIOScheduler)


@pytest.fixture(scope="function")
def notifications_repository(event_bus, logger):
    instance = NotificationsRepository(event_bus=event_bus, logger=logger, config=config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(event_bus, logger, notifications_repository):
    instance = EmailRepository(
        event_bus=event_bus, logger=logger, config=config, notifications_repository=notifications_repository
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository(logger, event_bus, notifications_repository):
    instance = BruinRepository(
        logger=logger,
        event_bus=event_bus,
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
def dri_repository(logger, event_bus, notifications_repository):
    instance = DRIRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def intermapper_monitor(
    event_bus,
    logger,
    scheduler,
    bruin_repository,
    notifications_repository,
    email_repository,
    metrics_repository,
    dri_repository,
    utils_repository,
):
    instance = InterMapperMonitor(
        event_bus=event_bus,
        logger=logger,
        scheduler=scheduler,
        config=config,
        bruin_repository=bruin_repository,
        notifications_repository=notifications_repository,
        email_repository=email_repository,
        utils_repository=utils_repository,
        dri_repository=dri_repository,
        metrics_repository=metrics_repository,
    )
    wrap_all_methods(instance)

    return instance
