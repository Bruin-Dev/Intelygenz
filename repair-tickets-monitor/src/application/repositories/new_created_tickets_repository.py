from typing import List


class NewCreatedTicketsRepository:
    def __init__(self, logger, config, storage_repository):
        self._logger = logger
        self._config = config
        self._storage_repository = storage_repository

    def get_pending_tickets(self) -> List[dict]:
        return self._storage_repository.find_all("archived_ticket_*")

    def mark_complete(self, email_id: str, ticket_id: str):
        self._logger.info(f"marking email complete '{email_id}' and '{ticket_id}' ")
        key = f"archived_ticket_{email_id}_{ticket_id}"
        self._storage_repository.remove(key)
