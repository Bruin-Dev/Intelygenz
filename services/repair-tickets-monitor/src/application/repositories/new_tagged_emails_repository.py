import logging
from dataclasses import dataclass
from typing import Any, List

from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


@dataclass
class NewTaggedEmailsRepository:
    _config: Any
    _storage_repository: StorageRepository

    def get_tagged_pending_emails(self) -> List[dict]:
        return self._storage_repository.find_all("tag_email_*")

    def get_email_details(self, email_id):
        key = f"archived_email_{email_id}"
        return self._storage_repository.get(key)

    def mark_complete(self, email_id: str):
        key = f"tag_email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        log.info(f"marking email complete '{email_id}'")
        self._storage_repository.remove(key, archive_key)
