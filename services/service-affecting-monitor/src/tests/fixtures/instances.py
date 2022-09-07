from unittest.mock import Mock

import pytest
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_repository import TemplateRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.trouble_repository import TroubleRepository
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
    instance = NotificationsRepository(event_bus=event_bus, config=config)
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
def velocloud_repository(logger, event_bus, utils_repository, notifications_repository):
    instance = VelocloudRepository(
        logger=logger,
        event_bus=event_bus,
        utils_repository=utils_repository,
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
def trouble_repository(utils_repository):
    instance = TroubleRepository(
        utils_repository=utils_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def ticket_repository(trouble_repository, utils_repository):
    instance = TicketRepository(
        trouble_repository=trouble_repository,
        utils_repository=utils_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def template_repository():
    instance = TemplateRepository(config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def service_affecting_monitor(
    logger,
    scheduler,
    customer_cache_repository,
    bruin_repository,
    velocloud_repository,
    notifications_repository,
    ticket_repository,
    trouble_repository,
    metrics_repository,
    utils_repository,
):
    instance = ServiceAffectingMonitor(
        logger=logger,
        scheduler=scheduler,
        config=config,
        bruin_repository=bruin_repository,
        velocloud_repository=velocloud_repository,
        customer_cache_repository=customer_cache_repository,
        notifications_repository=notifications_repository,
        ticket_repository=ticket_repository,
        trouble_repository=trouble_repository,
        metrics_repository=metrics_repository,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance
