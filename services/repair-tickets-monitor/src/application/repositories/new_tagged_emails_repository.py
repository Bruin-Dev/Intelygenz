from typing import List


class NewEmailsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository

    def get_tagged_pending_emails(self) -> List[dict]:
        return self._storage_repository.find_all("tag_email_*")

    def get_email_details(self, email_id):
        key = f"archived_email_{email_id}"
        return self._storage_repository.get(key)

    def mark_complete(self, email_id: str):
        key = f"tag_email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        self._logger.info(f"marking email complete '{email_id}'")
        self._storage_repository.remove(key, archive_key)
