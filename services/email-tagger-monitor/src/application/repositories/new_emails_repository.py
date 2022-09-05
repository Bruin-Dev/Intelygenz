import logging
from dataclasses import dataclass
from typing import Any, List

from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


@dataclass
class NewEmailsRepository:
    _config: Any
    _notifications_repository: NotificationsRepository
    _storage_repository: StorageRepository

    def get_pending_emails(self) -> List[dict]:
        return self._storage_repository.find_all("email_*")

    def save_new_email(self, email_data: dict):
        email_id = email_data["email"]["email_id"]
        key = f"email_{email_id}"
        log.info(f"saving email data '{email_id}'")
        self._storage_repository.save(key, email_data)

    def mark_complete(self, email_id: str):
        key = f"email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        log.info(f"marking email complete '{email_id}'")
        self._storage_repository.rename(key, archive_key)
        self._storage_repository.expire(archive_key, seconds=300)
