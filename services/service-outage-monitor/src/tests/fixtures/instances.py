from unittest.mock import Mock

import pytest
from application.actions.outage_monitoring import OutageMonitor
from application.actions.triage import Triage
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.digi_repository import DiGiRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.ha_repository import HaRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.outage_repository import OutageRepository
from application.repositories.triage_repository import TriageRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
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
def notifications_repository(event_bus):
    instance = NotificationsRepository(event_bus=event_bus)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(event_bus):
    instance = EmailRepository(event_bus=event_bus)
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
def velocloud_repository(logger, event_bus, notifications_repository):
    instance = VelocloudRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def customer_cache_repository(logger, event_bus, notifications_repository):
    instance = CustomerCacheRepository(
        logger=logger,
        event_bus=event_bus,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def triage_repository(utils_repository):
    instance = TriageRepository(
        config=config,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def outage_repository(logger, ha_repository):
    instance = OutageRepository(
        logger=logger,
        ha_repository=ha_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def digi_repository(event_bus, logger, notifications_repository):
    instance = DiGiRepository(
        event_bus=event_bus,
        logger=logger,
        config=config,
        notifications_repository=notifications_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def ha_repository(logger):
    instance = HaRepository(
        logger=logger,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def triage(
    event_bus,
    logger,
    scheduler,
    outage_repository,
    customer_cache_repository,
    bruin_repository,
    velocloud_repository,
    notifications_repository,
    triage_repository,
    metrics_repository,
    ha_repository,
):
    instance = Triage(
        event_bus=event_bus,
        logger=logger,
        scheduler=scheduler,
        config=config,
        outage_repository=outage_repository,
        customer_cache_repository=customer_cache_repository,
        bruin_repository=bruin_repository,
        velocloud_repository=velocloud_repository,
        notifications_repository=notifications_repository,
        triage_repository=triage_repository,
        ha_repository=ha_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def outage_monitor(
    event_bus,
    logger,
    scheduler,
    outage_repository,
    bruin_repository,
    velocloud_repository,
    notifications_repository,
    triage_repository,
    customer_cache_repository,
    metrics_repository,
    digi_repository,
    ha_repository,
    utils_repository,
    email_repository,
):
    instance = OutageMonitor(
        event_bus=event_bus,
        logger=logger,
        scheduler=scheduler,
        config=config,
        outage_repository=outage_repository,
        bruin_repository=bruin_repository,
        velocloud_repository=velocloud_repository,
        customer_cache_repository=customer_cache_repository,
        notifications_repository=notifications_repository,
        triage_repository=triage_repository,
        metrics_repository=metrics_repository,
        utils_repository=utils_repository,
        digi_repository=digi_repository,
        ha_repository=ha_repository,
        email_repository=email_repository,
    )
    wrap_all_methods(instance)

    return instance
