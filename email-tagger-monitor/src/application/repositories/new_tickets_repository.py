from typing import List


class NewTicketsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository

    def get_pending_tickets(self) -> List[dict]:
        return self._storage_repository.find_all("ticket_*")

    def save_new_ticket(self, email_data: dict, ticket_data: dict):
        email_id = email_data['email']['email_id']
        ticket_id = ticket_data['ticket_id']
        self._logger.info(f"adding email data '{email_id}' and '{ticket_id}'")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.save(key, {"email": email_data, "ticket": ticket_data})

    def mark_complete(self, email_id: str, ticket_id: str):
        self._logger.info(f"marking email complete '{email_id}' and '{ticket_id}' ")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.remove(key)
