from unittest.mock import Mock

from application.repositories.new_tagged_emails_repository import NewTaggedEmailsRepository
from config import testconfig as config


class TestNewTaggedEmailsRepository:
    def instance_test(self, storage_repository):
        new_tagged_emails_repository = NewTaggedEmailsRepository(
            config,
            storage_repository,
        )
        assert new_tagged_emails_repository._config == config
        assert new_tagged_emails_repository._storage_repository == storage_repository

    def get_tagged_pending_emails_test(self, new_tagged_emails_repository):
        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository
        new_tagged_emails_repository._storage_repository.find_all.return_value = []

        result = new_tagged_emails_repository.get_tagged_pending_emails()
        assert result == []

    def get_email_details_test(self, new_tagged_emails_repository):
        email_id = 1234
        key = f"archived_email_{email_id}"
        expected_result = {"email_id": email_id, "tag": 1234}

        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository
        new_tagged_emails_repository._storage_repository.get.return_value = expected_result

        result = new_tagged_emails_repository.get_email_details(email_id)

        assert result == expected_result
        storage_repository.get.assert_called_once_with(key)

    def mark_complete_test(self, new_tagged_emails_repository):
        email_id = 1234
        tag_key = f"tag_email_{email_id}"

        archive_key = f"archived_email_{email_id}"
        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository

        new_tagged_emails_repository.mark_complete(email_id)

        storage_repository.remove.assert_called_once_with(tag_key, archive_key)
