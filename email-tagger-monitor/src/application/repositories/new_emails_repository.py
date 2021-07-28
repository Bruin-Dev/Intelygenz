from typing import List


class NewEmailsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository
        self.EMAIL_PREFIX = self._config.MONITOR_CONFIG["prefixes"]["email_prefix"]

    def validate_email(self, email: dict) -> bool:
        if not email:
            return False
        elif 'email' not in email or not email['email'] or 'email_id' not in email['email']:
            return False

        return True

    def get_pending_emails(self) -> List[dict]:
        valid_emails = []
        all_emails = self._storage_repository.find_all(self.EMAIL_PREFIX)
        for email in all_emails:
            if self.validate_email(email):
                valid_emails.append(email)
            else:
                self._logger.info(f"Email not valid be processed. [{email}]")
        return valid_emails

    def save_new_email(self, email_data: dict):
        email_id = email_data['email']['email_id']
        key = f"email_{email_id}"
        self._logger.info(f"saving email data '{email_id}'")
        self._storage_repository.save(key, email_data)

    def mark_complete(self, email_id: str):
        key = f"email_{email_id}"
        self._logger.info(f"marking email complete '{email_id}'")
        self._storage_repository.remove(key)
