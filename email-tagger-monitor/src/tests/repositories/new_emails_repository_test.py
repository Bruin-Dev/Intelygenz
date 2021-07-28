from unittest.mock import Mock

from application.repositories.new_emails_repository import NewEmailsRepository
from config import testconfig


class TestEmailTaggerRepository:
    def instance_test(self):
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        storage_repository = Mock()

        new_emails_repository = NewEmailsRepository(logger, config, notifications_repository,
                                                    storage_repository)

        assert new_emails_repository._logger is logger
        assert new_emails_repository._config is config
        assert new_emails_repository._notifications_repository is notifications_repository
        assert new_emails_repository._storage_repository is storage_repository

    def validate_email_test(self, logger, notifications_repository, storage_repository):
        storage_repository.find_all = Mock(return_value=[])
        new_emails_repository = NewEmailsRepository(logger, testconfig, notifications_repository,
                                                    storage_repository)

        pending_emails = [
            {'email': {'email_id': '100', 'parent_id': '333'}},
            {'email': {'email_id': '101', 'parent_id': '334'}},
            {'email': {'email_id': '101'}},
            None,
            {'email': {'email': None}, 'ticket': None},
            {},
            {'email': {}, 'ticket': {}},
        ]
        expected_validations = [True, True, True, False, False, False, False]
        for expected_validation, email in zip(expected_validations, pending_emails):
            assert new_emails_repository.validate_email(email) == expected_validation

    def get_pending_emails_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.find_all = Mock(return_value=[])
        new_emails_repository = NewEmailsRepository(logger, testconfig, notifications_repository,
                                                    storage_repository)

        actual = new_emails_repository.get_pending_emails()

        storage_repository.find_all.assert_called_once()
        assert actual == []

    def save_new_email_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        new_emails_repository = NewEmailsRepository(logger, testconfig, notifications_repository,
                                                    storage_repository)

        expected_email_id = "email_123456"
        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "subject": "the title"
            }
        }
        response = new_emails_repository.save_new_email(email_data)

        storage_repository.save.assert_called_once_with(expected_email_id, email_data)
        assert response is None

    def mark_complete_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.remove = Mock()
        new_emails_repository = NewEmailsRepository(logger, testconfig, notifications_repository,
                                                    storage_repository)

        email_id = "123456"
        expected_email_id = "email_123456"
        response = new_emails_repository.mark_complete(email_id)

        storage_repository.remove.assert_called_once_with(expected_email_id)
        assert response is None
