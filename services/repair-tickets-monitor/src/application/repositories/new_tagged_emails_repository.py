import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from application.domain.email import Email, EmailTag
from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


@dataclass
class NewTaggedEmailsRepository:
    _config: Any
    _storage_repository: StorageRepository

    def get_tagged_pending_emails(self) -> List[Email]:
        raw_email_tags = self._storage_repository.find_all("tag_email_*")

        emails = []
        for raw_email_tag in raw_email_tags:
            email_id = raw_email_tag.get("email_id")
            raw_email = self.get_email_details(email_id).get("email")
            emails.append(self.to_email(raw_email, raw_email_tag))

        return emails

    def get_email_details(self, email_id):
        key = f"archived_email_{email_id}"
        return self._storage_repository.get(key)

    def mark_complete(self, email_id: str):
        key = f"tag_email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        log.info(f"marking email complete '{email_id}'")
        self._storage_repository.remove(key, archive_key)

    @staticmethod
    def to_email(raw_email: Dict[str, Any], raw_email_tag: Dict[str, Any]) -> Email:
        return Email(
            id=raw_email.get("email_id"),
            client_id=raw_email.get("client_id"),
            date=raw_email.get("date"),
            subject=raw_email.get("subject"),
            body=raw_email.get("body"),
            tag=EmailTag(type=raw_email_tag.get("tag_id"), probability=raw_email_tag.get("tag_probability")),
            sender_address=raw_email.get("from_address"),
            recipient_addresses=raw_email.get("to_address", []),
            cc_addresses=raw_email.get("send_cc", []),
            parent_id=raw_email.get("parent_id"),
            previous_id=raw_email.get("previous_id"),
        )
