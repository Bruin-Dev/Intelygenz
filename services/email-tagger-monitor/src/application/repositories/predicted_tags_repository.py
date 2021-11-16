from typing import List


class PredictedTagsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository

    def get_pending_tags(self) -> List[dict]:
        return self._storage_repository.find_all("tag_email_*")

    def save_new_tag(self, email_id: str, tag_id: str):
        key = f"tag_email_{email_id}"
        self._logger.info(f"saving predicted tag_id='{tag_id}' with email_id='{email_id}'")
        new_pred = {"email_id": email_id,
                    "tag_id": tag_id}
        self._storage_repository.save(key, new_pred)

    def mark_complete(self, email_id: str):
        key = f"tag_email_{email_id}"
        self._logger.info(f"marking tag complete with email_id='{email_id}'")
        self._storage_repository.remove(key)
