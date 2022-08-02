from datetime import datetime
from typing import List
from unittest.mock import Mock

from framework.storage.model import Email, EmailMetadata, EmailStorage, EmailTag
from pydantic import Field
from redis.client import Redis


def email_metadata_model_is_properly_initialized_test():
    assert EmailMetadata().utc_creation_datetime <= datetime.utcnow()


def emails_are_properly_stored_test():
    redis = Mock(Redis)
    email = AnyEmail(id="any_id")
    email_storage = EmailStorage(redis=redis, environment="any_environment", data_name="any_name")

    email_storage.store(email)

    redis.set.assert_called_once_with("any_environment:any_name:any_id", email.json(), ex=None)


def emails_are_properly_deleted_test():
    redis = Mock(Redis)
    email = AnyEmail(id="any_id")
    email_storage = EmailStorage(redis=redis, environment="any_environment", data_name="any_name")

    email_storage.delete(email)

    redis.delete.assert_called_once_with("any_environment:any_name:any_id")


class AnyEmailTag(EmailTag):
    type: str = "any_type"
    probability: float = hash("any_probability")


class AnyEmail(Email):
    id: str = "any_id"
    client_id: str = "any_client_id"
    date: datetime = Field(default_factory=lambda: datetime.utcnow())
    subject: str = "any_subject"
    body: str = "any_body"
    sender_address: str = "any_sender_address"
    recipient_addresses: List[str] = Field(default_factory=lambda: ["any_recipient_address"])
    cc_addresses: List[str] = Field(default_factory=lambda: ["any_cc_address"])
    tag: EmailTag = Field(default_factory=lambda: AnyEmailTag())
