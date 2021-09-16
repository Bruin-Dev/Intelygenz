from typing import List


class RepairTicketsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository

    def get_pending_repair_emails(self) -> List[dict]:
        return self._storage_repository.find_all("email_rta_*")

    def get_feedback_emails(self) -> List[dict]:
        # TODO: retrieve file for a concrete day o range of dates from S3
        return []

    # def save_new_email(self, email_data: dict):
    #     email_id = email_data['email']['email_id']
    #     key = f"email_{email_id}"
    #     self._logger.info(f"saving email data '{email_id}'")
    #     self._storage_repository.save(key, email_data)

    # def mark_complete(self, email_id: str):
    #     key = f"email_{email_id}"
    #     self._logger.info(f"marking email complete '{email_id}'")
    #     self._storage_repository.remove(key)
