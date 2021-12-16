from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from config import testconfig as config


class TestNewCreatedTicketsRepository:

    def instance_test(self, logger, storage_repository):

        new_created_tickets_repository = NewCreatedTicketsRepository(
            logger,
            config,
            storage_repository
        )

        assert new_created_tickets_repository._logger is logger
        assert new_created_tickets_repository._config is config
        assert new_created_tickets_repository._storage_repository is storage_repository

    def get_pending_tickets_test(self, storage_repository, new_created_tickets_repository):
        storage_repository.find_all.return_value = []
        actual = new_created_tickets_repository.get_pending_tickets()

        storage_repository.find_all.assert_called_once()
        assert actual == []

    def increase_ticket_error_counter_test(self, storage_repository, new_created_tickets_repository):
        ticket_id = 45345
        error_code = 404

        new_created_tickets_repository.increase_ticket_error_counter(ticket_id, error_code)
        key = f"archive_error_{error_code}_ticket_{ticket_id}"

        storage_repository.increment.assert_called_once_with(key)

    def delete_ticket_error_counter_test(self, storage_repository, new_created_tickets_repository):
        ticket_id = 45345
        error_code = 404

        key = f"archive_error_{error_code}_ticket_{ticket_id}"

        new_created_tickets_repository.delete_ticket_error_counter(ticket_id, error_code)

        storage_repository.remove.assert_called_once_with(key)

    def mark_complete_ok_test(self, storage_repository, new_created_tickets_repository):
        email_id = "12345"
        ticket_id = "67890"
        expected_archive_id = f"archived_ticket_{email_id}_{ticket_id}"
        response = new_created_tickets_repository.mark_complete(email_id, ticket_id)

        storage_repository.remove.assert_called_once_with(expected_archive_id)
        assert response is None
