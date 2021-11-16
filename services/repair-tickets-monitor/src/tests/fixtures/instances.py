import pytest
from asynctest import create_autospec
from igz.packages.eventbus.eventbus import EventBus
from tests.fixtures._helpers import wrap_all_methods
from unittest.mock import Mock

from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository
from application.actions.new_created_tickets_feedback import NewCreatedTicketsFeedback
from config import testconfig as config


@pytest.fixture(scope='function')
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def redis():
    return Mock()


@pytest.fixture(scope='function')
def scheduler():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository(event_bus):
    instance = NotificationsRepository(event_bus=event_bus)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def bruin_repository(event_bus, logger, notifications_repository):
    instance = BruinRepository(event_bus, logger, config, notifications_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def storage_repository(logger, redis):
    instance = StorageRepository(config, logger, redis)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope='function')
def new_created_tickets_repository(logger, storage_repository):
    return NewCreatedTicketsRepository(
        logger,
        config,
        storage_repository
    )


@pytest.fixture(scope='function')
def repair_ticket_kre_repository(event_bus, logger, notifications_repository):
    return RepairTicketKreRepository(event_bus, logger, config, notifications_repository)


@pytest.fixture(scope='function')
def new_created_tickets_feedback(
        event_bus,
        logger,
        scheduler,
        new_created_tickets_repository,
        repair_ticket_kre_repository,
        bruin_repository
):
    return NewCreatedTicketsFeedback(
        event_bus,
        logger,
        scheduler,
        config,
        new_created_tickets_repository,
        repair_ticket_kre_repository,
        bruin_repository
    )
