from unittest.mock import Mock

import pytest
from application.actions.get_emails import GetEmails
from application.actions.mark_email_as_read import MarkEmailAsRead
from application.actions.send_to_email import SendToEmail
from application.clients.email_client import EmailClient
from application.clients.email_reader_client import EmailReaderClient
from application.repositories.email_reader_repository import EmailReaderRepository
from application.repositories.email_repository import EmailRepository
from asynctest import create_autospec
from config import testconfig
from igz.packages.eventbus.eventbus import EventBus
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger():
    # Let's suppress all logs in tests
    return Mock()


@pytest.fixture(scope="function")
def event_bus():
    return create_autospec(EventBus)


@pytest.fixture(scope="function")
def email_client(logger) -> EmailClient:
    instance = EmailClient(logger=logger, config=testconfig)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(logger, email_client) -> EmailRepository:
    instance = EmailRepository(logger=logger, config=testconfig, email_client=email_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def send_to_email_action(logger, email_repository, event_bus) -> SendToEmail:
    instance = SendToEmail(logger=logger, config=testconfig, email_repository=email_repository, event_bus=event_bus)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_reader_client(logger) -> EmailReaderClient:
    instance = EmailReaderClient(logger=logger, config=testconfig)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_reader_repository(logger, email_reader_client) -> EmailReaderRepository:
    instance = EmailReaderRepository(logger=logger, config=testconfig, email_reader_client=email_reader_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def get_emails_action(logger, email_reader_repository, event_bus) -> GetEmails:
    instance = GetEmails(
        logger=logger, config=testconfig, email_reader_repository=email_reader_repository, event_bus=event_bus
    )
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def mark_email_as_read_action(logger, email_reader_repository, event_bus) -> MarkEmailAsRead:
    instance = MarkEmailAsRead(
        logger=logger, config=testconfig, email_reader_repository=email_reader_repository, event_bus=event_bus
    )
    wrap_all_methods(instance)

    return instance
