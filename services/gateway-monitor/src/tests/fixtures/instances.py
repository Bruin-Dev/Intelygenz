from unittest.mock import Mock

import pytest
from application.actions.monitoring import Monitor
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.servicenow_repository import ServiceNowRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from asynctest import CoroutineMock
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def event_bus() -> Mock:
    event_bus = Mock()
    event_bus.publish_message = CoroutineMock()
    return event_bus


@pytest.fixture(scope="function")
def scheduler() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def metrics_repository() -> MetricsRepository:
    instance = MetricsRepository()
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def utils_repository() -> UtilsRepository:
    instance = UtilsRepository()
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def notifications_repository(event_bus) -> NotificationsRepository:
    instance = NotificationsRepository(event_bus)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def velocloud_repository(event_bus, logger, notifications_repository) -> VelocloudRepository:
    instance = VelocloudRepository(event_bus, logger, testconfig, notifications_repository)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def servicenow_repository(event_bus, logger, notifications_repository) -> ServiceNowRepository:
    instance = ServiceNowRepository(event_bus, logger, testconfig, notifications_repository)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def monitor(
    event_bus,
    logger,
    scheduler,
    metrics_repository,
    servicenow_repository,
    velocloud_repository,
    notifications_repository,
    utils_repository,
) -> Monitor:
    instance = Monitor(
        event_bus,
        logger,
        scheduler,
        testconfig,
        metrics_repository,
        servicenow_repository,
        velocloud_repository,
        notifications_repository,
        utils_repository,
    )
    wrap_all_methods(instance)
    return instance
