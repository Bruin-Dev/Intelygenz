from typing import List


class NewCreatedTicketsRepository:
    def __init__(self, logger, config, storage_repository):
        self._logger = logger
        self._config = config
        self._storage_repository = storage_repository

    def get_pending_tickets(self) -> List[dict]:
        """Gets a list of all pending tickets

        Returns:
            [list]: list of pending tickets.
        """
        return self._storage_repository.find_all("archived_ticket_*")

    def increase_ticket_error_counter(self, ticket_id: int, error_code: int):
        """Increment a redis value by one and return the updated value.

        Args:
            ticket_id (int): The ticket_id used on the storage key
            error_code (int): The error_code used on the storage key

        Returns:
            [int]: Incremented value
        """
        self._logger.info(f"increasing error={error_code} for ticket id={ticket_id}")
        key = f"archive_error_{error_code}_ticket_{ticket_id}"
        return self._storage_repository.increment(key)

    def delete_ticket_error_counter(self, ticket_id: int, error_code: int):
        """Remove the storage ticket error counter.

        Args:
            ticket_id (int): [description]
            error_code (int): [description]
        """
        self._logger.info(f"removing counter for error={error_code} for ticket id={ticket_id}")
        key = f"archived_error_{error_code}_ticket_{ticket_id}"
        self._storage_repository.remove(key)

    def mark_complete(self, email_id: str, ticket_id: str):
        """Remove an already completed ticket

        Args:
            email_id (str): email identification.
            ticket_id (str): ticket identification.
        """
        self._logger.info(f"marking email complete '{email_id}' and '{ticket_id}' ")
        key = f"archived_ticket_{email_id}_{ticket_id}"
        self._storage_repository.remove(key)
