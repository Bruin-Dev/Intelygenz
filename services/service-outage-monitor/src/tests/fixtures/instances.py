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
from config import testconfig as config
from framework.nats.client import Client as NatsClient
from framework.storage.task_dispatcher_client import TaskDispatcherClient
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
def task_dispatcher_client():
    return Mock(spec_set=TaskDispatcherClient)


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    instance = NotificationsRepository(nats_client=nats_client)
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
def velocloud_repository(nats_client, notifications_repository):
    instance = VelocloudRepository(
        nats_client=nats_client,
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
def triage_repository(utils_repository):
    instance = TriageRepository(config=config, utils_repository=utils_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def utils_repository():
    instance = UtilsRepository()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def outage_repository(ha_repository):
    instance = OutageRepository(ha_repository=ha_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def digi_repository(nats_client, notifications_repository):
    instance = DiGiRepository(
        nats_client=nats_client,
        config=config,
        notifications_repository=notifications_repository,
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def ha_repository():
    instance = HaRepository(config=config)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def triage(
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
    scheduler,
    task_dispatcher_client,
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
        scheduler=scheduler,
        task_dispatcher_client=task_dispatcher_client,
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
