from unittest.mock import AsyncMock, Mock, create_autospec

import pytest
from application.actions.new_closed_tickets_feedback import NewClosedTicketsFeedback
from application.actions.new_created_tickets_feedback import NewCreatedTicketsFeedback
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from application.repositories.new_tagged_emails_repository import NewTaggedEmailsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from application.repositories.storage_repository import StorageRepository
from config import testconfig as config
from framework.nats.client import Client as NatsClient
from framework.storage.model import RepairParentEmailStorage
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(NatsClient)


@pytest.fixture(scope="function")
def event_bus_real(redis):
    return create_autospec(NatsClient)


@pytest.fixture(scope="function")
def logger():
    return Mock()


@pytest.fixture(scope="function")
def redis():
    return Mock()


@pytest.fixture(scope="function")
def scheduler():
    return Mock()


@pytest.fixture(scope="function")
def notifications_repository(event_bus):
    instance = NotificationsRepository(_event_bus=event_bus)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository(event_bus, notifications_repository):
    instance = BruinRepository(event_bus, config, notifications_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def bruin_repository_real(event_bus_real, notifications_repository):
    return BruinRepository(event_bus_real, config, notifications_repository)


@pytest.fixture(scope="function")
def parent_email_storage(redis):
    return RepairParentEmailStorage(redis=redis, environment=config.CURRENT_ENVIRONMENT)


@pytest.fixture(scope="function")
def storage_repository(redis):
    instance = StorageRepository(config, redis)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def new_created_tickets_repository(storage_repository):
    return NewCreatedTicketsRepository(config, storage_repository)


@pytest.fixture(scope="function")
def new_tagged_emails_repository(storage_repository, parent_email_storage):
    return NewTaggedEmailsRepository(config, storage_repository, parent_email_storage)


@pytest.fixture(scope="function")
def repair_ticket_kre_repository(event_bus, notifications_repository):
    return RepairTicketKreRepository(event_bus, config, notifications_repository)


@pytest.fixture(scope="function")
def new_created_tickets_feedback(
    event_bus, scheduler, new_created_tickets_repository, repair_ticket_kre_repository, bruin_repository
):
    return NewCreatedTicketsFeedback(
        event_bus,
        scheduler,
        config,
        new_created_tickets_repository,
        repair_ticket_kre_repository,
        bruin_repository,
    )


@pytest.fixture(scope="function")
def repair_tickets_monitor(
    event_bus, scheduler, bruin_repository_real, new_tagged_emails_repository, repair_ticket_kre_repository
):
    return RepairTicketsMonitor(
        event_bus,
        scheduler,
        config,
        bruin_repository_real,
        new_tagged_emails_repository,
        repair_ticket_kre_repository,
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
        AsyncMock(),
    )


@pytest.fixture(scope="function")
def new_closed_tickets_feedback(event_bus, scheduler, repair_ticket_kre_repository, bruin_repository):
    return NewClosedTicketsFeedback(event_bus, scheduler, config, repair_ticket_kre_repository, bruin_repository)
