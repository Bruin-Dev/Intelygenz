import logging
from dataclasses import dataclass
from typing import Any, List, Optional

from framework.storage.model import RepairParentEmailStorage
from framework.storage.model.email_storage import Email as RedisEmail
from framework.storage.model.email_storage import EmailTag as RedisEmailTag
from pydantic import BaseModel

from application.domain.email import Email, EmailTag
from application.repositories.storage_repository import StorageRepository

log = logging.getLogger(__name__)


class LegacyRedisEmail(BaseModel):
    email_id: int
    client_id: int
    date: str
    subject: str
    body: str
    from_address: str
    to_address: List[str]
    send_cc: Optional[List[str]]
    parent_id: Optional[int]


class LegacyRedisEmailTag(BaseModel):
    email_id: int
    tag_id: int
    tag_probability: float


@dataclass
class NewTaggedEmailsRepository:
    _config: Any
    _storage_repository: StorageRepository
    _parent_email_storage: RepairParentEmailStorage

    def get_tagged_pending_emails(self) -> List[Email]:
        dict_email_tags = self._storage_repository.find_all("tag_email_*")

        emails = []
        for dict_email_tag in dict_email_tags:
            legacy_email_tag = LegacyRedisEmailTag.parse_obj(dict_email_tag)
            dict_email = self.get_email_details(legacy_email_tag.email_id).get("email")
            legacy_email = LegacyRedisEmail.parse_obj(dict_email)
            redis_email = self.map_legacy_email(legacy_email, legacy_email_tag)

            email = self.deserialize_email(redis_email)
            if redis_email.parent_id is not None:
                redis_parent_email = self._parent_email_storage.find(redis_email.parent_id)
                if redis_parent_email:
                    email.parent = self.deserialize_email(redis_parent_email)

            emails.append(email)

        return emails

    def get_email_details(self, email_id):
        key = f"archived_email_{email_id}"
        return self._storage_repository.get(key)

    def mark_complete(self, email_id: str):
        key = f"tag_email_{email_id}"
        archive_key = f"archived_email_{email_id}"
        log.info(f"marking email complete '{email_id}'")
        self._storage_repository.remove(key, archive_key)

    def save_parent_email(self, email: Email):
        self._parent_email_storage.store(self.serialize_email(email))

    def remove_parent_email(self, email: Email):
        self._parent_email_storage.delete(email)

    @staticmethod
    def serialize_email(email: Email) -> RedisEmail:
        return RedisEmail(
            id=email.id,
            client_id=email.client_id,
            date=email.date,
            subject=email.subject,
            body=email.body,
            sender_address=email.sender_address,
            recipient_addresses=email.recipient_addresses,
            cc_addresses=email.cc_addresses,
            parent_id=email.parent.id if email.parent else None,
            tag=RedisEmailTag(type=email.tag.type, probability=email.tag.probability),
        )

    @staticmethod
    def deserialize_email(redis_email: RedisEmail):
        return Email(
            id=redis_email.id,
            client_id=redis_email.client_id,
            date=redis_email.date,
            subject=redis_email.subject,
            body=redis_email.body,
            sender_address=redis_email.sender_address,
            recipient_addresses=redis_email.recipient_addresses,
            cc_addresses=redis_email.cc_addresses,
            tag=EmailTag(type=redis_email.tag.type, probability=redis_email.tag.probability),
        )

    @staticmethod
    def map_legacy_email(legacy_email: LegacyRedisEmail, legacy_email_tag: LegacyRedisEmailTag) -> RedisEmail:
        return RedisEmail(
            id=legacy_email.email_id,
            client_id=legacy_email.client_id,
            parent_id=legacy_email.parent_id,
            date=legacy_email.date,
            subject=legacy_email.subject,
            body=legacy_email.body,
            sender_address=legacy_email.from_address,
            recipient_addresses=legacy_email.to_address,
            cc_addresses=legacy_email.send_cc if legacy_email.send_cc else [],
            tag=RedisEmailTag(type=legacy_email_tag.tag_id, probability=legacy_email_tag.tag_probability),
        )
