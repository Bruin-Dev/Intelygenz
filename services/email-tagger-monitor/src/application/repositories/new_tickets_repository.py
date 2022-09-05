import logging
from dataclasses import dataclass
from typing import Any, List

from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


@dataclass
class NewTicketsRepository:
    _config: Any
    _notifications_repository: NotificationsRepository
    _storage_repository: StorageRepository

    @staticmethod
    def validate_ticket(ticket: dict) -> bool:
        if not ticket:
            return False
        elif "email" not in ticket or not ticket["email"] or "ticket" not in ticket or not ticket["ticket"]:
            return False
        elif "email" not in ticket["email"] or not ticket["email"]["email"]:
            return False
        elif ("email_id" not in ticket["email"]["email"] or not ticket["email"]["email"]["email_id"]) or (
            "client_id" not in ticket["email"]["email"] or not ticket["email"]["email"]["client_id"]
        ):
            return False
        elif "ticket_id" not in ticket["ticket"] or not ticket["ticket"]["ticket_id"]:
            return False

        return True

    def get_pending_tickets(self) -> List[dict]:
        return self._storage_repository.find_all("ticket_*")

    def increase_ticket_error_counter(self, ticket_id: int, error_code: int):
        """Increment a redis value by one and return the updated value.

        Args:
            ticket_id (int): The ticket_id used on the storage key
            error_code (int): The error_code used on the storage key

        Returns:
            [int]: Incremented value
        """
        log.info(f"increasing error={error_code} for ticket id={ticket_id}")
        key = f"error_{error_code}_ticket_{ticket_id}"
        return self._storage_repository.increment(key)

    def delete_ticket_error_counter(self, ticket_id: int, error_code: int):
        """Remove the storage ticket error counter.

        Args:
            ticket_id (int): [description]
            error_code (int): [description]
        """
        log.info(f"removing counter for error={error_code} for ticket id={ticket_id}")
        key = f"error_{error_code}_ticket_{ticket_id}"
        self._storage_repository.remove(key)

    def delete_ticket(self, email_id: str, ticket_id: int):
        log.info(f"deleting ticket_id={ticket_id}")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.remove(key)

    def save_new_ticket(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email"]["email_id"]
        ticket_id = ticket_data["ticket_id"]
        log.info(f"adding email data '{email_id}' and '{ticket_id}'")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.save(key, {"email": email_data, "ticket": ticket_data})

    def mark_complete(self, email_id: str, ticket_id: str):
        log.info(f"marking email complete '{email_id}' and '{ticket_id}' ")
        key = f"ticket_{email_id}_{ticket_id}"
        archive_key = f"archived_ticket_{email_id}_{ticket_id}"
        self._storage_repository.rename(key, archive_key)
        self._storage_repository.expire(archive_key, seconds=300)
