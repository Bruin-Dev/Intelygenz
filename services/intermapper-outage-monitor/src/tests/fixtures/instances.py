from unittest.mock import Mock

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.nats.client import Client as NatsClient

from application.actions.intermapper_monitoring import InterMapperMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.dri_repository import DRIRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository
from config import testconfig as config
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def metrics_repository():
    # Let's fake this repository so we don't depend on a metrics server to write stuff for Prometheus
    return Mock()


@pytest.fixture(scope="function")
def nats_client():
    return Mock(spec_set=NatsClient)


@pytest.fixture(scope="function")
def scheduler():
    return Mock(spec_set=AsyncIOScheduler)


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client, config=config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(nats_client, notifications_repository):
    instance = EmailRepository(
        nats_client=nats_client, config=config, notifications_repository=notifications_repository
    )
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
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def dri_repository(nats_client, notifications_repository):
    instance = DRIRepository(
        nats_client=nats_client,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def intermapper_monitor(
    nats_client,
    scheduler,
    bruin_repository,
    notifications_repository,
    email_repository,
    metrics_repository,
    dri_repository,
    utils_repository,
):
    instance = InterMapperMonitor(
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
