from unittest.mock import Mock

import pytest
from framework.nats.client import Client

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
from config import testconfig as config
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def metrics_repository():
    # Let's fake this repository so we don't depend on a metrics server to write stuff for Prometheus
    return Mock()


@pytest.fixture(scope="function")
def nats_client():
    return Mock(spec_set=Client)


@pytest.fixture(scope="function")
def scheduler():
    return Mock()


@pytest.fixture(scope="function")
def task_dispatcher_client():
    return Mock()


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client, config=config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(nats_client):
    instance = EmailRepository(nats_client=nats_client)
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
def velocloud_repository(nats_client, utils_repository, notifications_repository):
    instance = VelocloudRepository(
        nats_client=nats_client,
        utils_repository=utils_repository,
        notifications_repository=notifications_repository,
        config=config,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def customer_cache_repository(nats_client, notifications_repository):
    instance = CustomerCacheRepository(
        nats_client=nats_client,
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
    scheduler,
    task_dispatcher_client,
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
        scheduler=scheduler,
        task_dispatcher_client=task_dispatcher_client,
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
