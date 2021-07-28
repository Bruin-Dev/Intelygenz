import pytest
from unittest.mock import Mock

from application.repositories.new_tickets_repository import NewTicketsRepository
from config import testconfig


class TestEmailTaggerRepository:
    def instance_test(self):
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        storage_repository = Mock()

        new_emails_repository = NewTicketsRepository(logger, config, notifications_repository,
                                                     storage_repository)

        assert new_emails_repository._logger is logger
        assert new_emails_repository._config is config
        assert new_emails_repository._notifications_repository is notifications_repository
        assert new_emails_repository._storage_repository is storage_repository

    def validate_ticket_test(self, logger, notifications_repository, storage_repository):
        new_tickets_repository = NewTicketsRepository(logger, testconfig, notifications_repository,
                                                      storage_repository)

        pending_tickets = [
            {'email': {'email': {'email_id': '100', 'client_id': '333'}}, 'ticket': {'ticket_id': 200}},
            {'email': {'email': {'email_id': '101', 'client_id': '333'}}, 'ticket': {'ticket_id': 201}},
            None,
            {'email': None, 'ticket': {'ticket_id': 201}},
            {'email': {'email': {'email_id': '101', 'client_id': '333'}}, 'ticket': None},
            {'email': {'email': {'email_id': None, 'client_id': '333'}}, 'ticket': None},
            {'email': {'email': None}, 'ticket': None},
            {},
            {'email': {}, 'ticket': {}},
        ]
        expected_validations = [True, True, False, False, False, False, False, False, False]
        for expected_validation, ticket in zip(expected_validations, pending_tickets):
            assert new_tickets_repository.validate_ticket(ticket) == expected_validation

    def get_pending_emails_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.find_all = Mock(return_value=[])
        new_emails_repository = NewTicketsRepository(logger, testconfig, notifications_repository,
                                                     storage_repository)

        actual = new_emails_repository.get_pending_tickets()

        storage_repository.find_all.assert_called_once()
        assert actual == []

    def save_new_email_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        new_emails_repository = NewTicketsRepository(logger, testconfig, notifications_repository,
                                                     storage_repository)

        expected_id = "ticket_12345_67890"
        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "12345",
                "subject": "the title"
            }
        }
        ticket_data = {
            "ticket_id": "67890",
            "call_type": "CHG",
            "category": "AAC",
            "ticket_creation_date": "2016-08-29T09:12:33.001Z"
        }

        response = new_emails_repository.save_new_ticket(email_data, ticket_data)

        storage_repository.save.assert_called_once_with(expected_id, {"email": email_data, "ticket": ticket_data})
        assert response is None

    def mark_complete_ok_test(self, logger, notifications_repository, storage_repository):
        storage_repository.remove = Mock()
        new_emails_repository = NewTicketsRepository(logger, testconfig, notifications_repository,
                                                     storage_repository)

        email_id = "12345"
        ticket_id = "67890"
        expected_id = "ticket_12345_67890"
        response = new_emails_repository.mark_complete(email_id, ticket_id)

        storage_repository.remove.assert_called_once_with(expected_id)
        assert response is None
