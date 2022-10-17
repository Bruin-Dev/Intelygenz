from unittest.mock import Mock

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from framework.nats.client import Client as NatsClient

from application.actions.fraud_monitoring import FraudMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.ticket_repository import TicketRepository
from application.repositories.utils_repository import UtilsRepository
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def nats_client():
    return Mock(spec_set=NatsClient)


@pytest.fixture(scope="function")
def scheduler():
    return Mock(spec_set=AsyncIOScheduler)


@pytest.fixture(scope="function")
def metrics_repository():
    instance = MetricsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client, config=testconfig)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(nats_client, notifications_repository):
    instance = EmailRepository(
        nats_client=nats_client, config=testconfig, notifications_repository=notifications_repository
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository(nats_client, notifications_repository):
    instance = BruinRepository(
        nats_client=nats_client,
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
    nats_client,
    scheduler,
    metrics_repository,
    notifications_repository,
    email_repository,
    bruin_repository,
    ticket_repository,
    utils_repository,
):
    instance = FraudMonitor(
        nats_client=nats_client,
        scheduler=scheduler,
        config=testconfig,
        metrics_repository=metrics_repository,
        notifications_repository=notifications_repository,
        email_repository=email_repository,
        bruin_repository=bruin_repository,
        ticket_repository=ticket_repository,
        utils_repository=utils_repository,
    )
    wrap_all_methods(instance)

    return instance
