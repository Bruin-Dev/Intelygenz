import logging
from dataclasses import dataclass
from typing import Any, List

from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


@dataclass
class PredictedTagsRepository:
    _config: Any
    _notifications_repository: NotificationsRepository
    _storage_repository: StorageRepository

    def get_pending_tags(self) -> List[dict]:
        return self._storage_repository.find_all("tag_email_*")

    def save_new_tag(self, email_id: str, tag_id: str, tag_probability: float):
        key = f"tag_email_{email_id}"
        log.info(f"saving predicted tag_id='{tag_id}' with email_id='{email_id}'")
        new_pred = {
            "email_id": email_id,
            "tag_id": tag_id,
            "tag_probability": tag_probability,
        }
        self._storage_repository.save(key, new_pred)
        self._storage_repository.expire(key, seconds=300)
