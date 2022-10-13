from unittest.mock import AsyncMock, Mock

import pytest

from application.actions.monitoring import Monitor
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.servicenow_repository import ServiceNowRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def nats_client() -> Mock:
    return Mock()


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
def notifications_repository(nats_client) -> NotificationsRepository:
    instance = NotificationsRepository(nats_client)
    return instance


@pytest.fixture(scope="function")
def velocloud_repository(nats_client, notifications_repository) -> VelocloudRepository:
    instance = VelocloudRepository(
        nats_client=nats_client, config=testconfig, notifications_repository=notifications_repository
    )
    return instance


@pytest.fixture(scope="function")
def servicenow_repository(nats_client, notifications_repository) -> ServiceNowRepository:
    instance = ServiceNowRepository(
        nats_client=nats_client, config=testconfig, notifications_repository=notifications_repository
    )
    return instance


@pytest.fixture(scope="function")
def monitor(
    scheduler,
    metrics_repository,
    servicenow_repository,
    velocloud_repository,
    notifications_repository,
    utils_repository,
) -> Monitor:
    instance = Monitor(
        scheduler=scheduler,
        config=testconfig,
        metrics_repository=metrics_repository,
        servicenow_repository=servicenow_repository,
        velocloud_repository=velocloud_repository,
        notifications_repository=notifications_repository,
        utils_repository=utils_repository,
    )
    return instance
