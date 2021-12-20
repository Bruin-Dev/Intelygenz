from typing import List


class NewEmailsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository

    def get_pending_emails(self) -> List[dict]:
        return self._storage_repository.find_all("email_*")

    def save_new_email(self, email_data: dict):
        email_id = email_data['email']['email_id']
        key = f"email_{email_id}"
        self._logger.info(f"saving email data '{email_id}'")
        self._storage_repository.save(key, email_data)

    def mark_complete(self, email_id: str):
        key = f"email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        self._logger.info(f"marking email complete '{email_id}'")
        self._storage_repository.rename(key, archive_key)
        self._storage_repository.expire(archive_key, seconds=300)
