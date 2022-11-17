from unittest.mock import Mock

import pytest
from application.repositories.new_emails_repository import NewEmailsRepository
from config import testconfig


@pytest.fixture
def new_emails_repository(storage_repository, notifications_repository):
    return NewEmailsRepository(
        testconfig,
        notifications_repository,
        storage_repository,
    )


class TestNewEmailsRepository:
    def instance_test(self):
        config = testconfig
        notifications_repository = Mock()
        storage_repository = Mock()

        new_emails_repository = NewEmailsRepository(config, notifications_repository, storage_repository)

        assert new_emails_repository._config is config
        assert new_emails_repository._notifications_repository is notifications_repository
        assert new_emails_repository._storage_repository is storage_repository

    def get_pending_emails_ok_test(self, storage_repository, new_emails_repository):
        storage_repository.find_all = Mock(return_value=[])

        actual = new_emails_repository.get_pending_emails()

        storage_repository.find_all.assert_called_once()
        assert actual == []

    def save_new_email_ok_test(self, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        new_emails_repository = NewEmailsRepository(testconfig, notifications_repository, storage_repository)

        expected_email_id = "email_123456"
        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            }
        }
        response = new_emails_repository.save_new_email(email_data)

        storage_repository.save.assert_called_once_with(expected_email_id, email_data)
        assert response is None

    def save_new_parent_email_ok_test(self, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        new_emails_repository = NewEmailsRepository(testconfig, notifications_repository, storage_repository)

        expected_email_id = "email_123456"
        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            }
        }
        response = new_emails_repository.save_new_email(email_data)

        storage_repository.save.assert_called_once_with(expected_email_id, email_data)
        assert response is None

    def save_new_reply_email_ok_test(self, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        new_emails_repository = NewEmailsRepository(testconfig, notifications_repository, storage_repository)

        expected_email_id = "email_123456"
        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title",
            }
        }
        response = new_emails_repository.save_new_email(email_data)

        storage_repository.save.assert_called_once_with(expected_email_id, email_data)
        assert response is None

    def mark_complete_ok_test(self, notifications_repository, storage_repository):
        storage_repository.rename = Mock()
        storage_repository.expire = Mock()
        new_emails_repository = NewEmailsRepository(testconfig, notifications_repository, storage_repository)

        email_id = "123456"
        expected_email_id = "email_123456"
        expected_archive_id = "archived_email_123456"

        response = new_emails_repository.mark_complete(email_id)

        storage_repository.rename.assert_called_once_with(expected_email_id, expected_archive_id)
        storage_repository.expire.assert_called_once_with(expected_archive_id, seconds=300)
        assert response is None
