import pytest

from application.actions.get_emails import GetEmails
from application.actions.mark_email_as_read import MarkEmailAsRead
from application.actions.send_to_email import SendToEmail
from application.clients.email_client import EmailClient
from application.clients.email_reader_client import EmailReaderClient
from application.repositories.email_reader_repository import EmailReaderRepository
from application.repositories.email_repository import EmailRepository
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def email_client() -> EmailClient:
    instance = EmailClient(config=testconfig)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_repository(email_client) -> EmailRepository:
    instance = EmailRepository(email_client=email_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def send_to_email_action(email_repository) -> SendToEmail:
    instance = SendToEmail(email_repository=email_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_reader_client() -> EmailReaderClient:
    instance = EmailReaderClient()
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def email_reader_repository(email_reader_client) -> EmailReaderRepository:
    instance = EmailReaderRepository(config=testconfig, email_reader_client=email_reader_client)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def get_emails_action(email_reader_repository) -> GetEmails:
    instance = GetEmails(email_reader_repository=email_reader_repository)
    wrap_all_methods(instance)

    return instance


@pytest.fixture(scope="function")
def mark_email_as_read_action(email_reader_repository) -> MarkEmailAsRead:
    instance = MarkEmailAsRead(email_reader_repository=email_reader_repository)
    wrap_all_methods(instance)

    return instance
