from datetime import datetime, timezone
from typing import List
from unittest.mock import Mock, patch

from framework.storage.model.email_storage import Email as RedisEmail
from framework.storage.model.email_storage import EmailTag as RedisEmailTag
from framework.storage.model.email_storage import RepairParentEmailStorage
from framework.testing import given
from pydantic import Field
from pytz import UTC

from application.domain.email import Email, EmailTag
from application.repositories.new_tagged_emails_repository import (
    LegacyRedisEmail,
    LegacyRedisEmailTag,
    NewTaggedEmailsRepository,
)
from application.repositories.storage_repository import StorageRepository
from config import testconfig as config
from tests.fixtures.domain import AnyEmail


class FooDatetime(datetime):
    @classmethod
    def utcnow(cls):
        return datetime(2000, 1, 1, 0, 0, 0)


class TestNewTaggedEmailsRepository:
    def instance_test(self, storage_repository, parent_email_storage):
        new_tagged_emails_repository = NewTaggedEmailsRepository(
            config,
            storage_repository,
            parent_email_storage,
        )
        assert new_tagged_emails_repository._config == config
        assert new_tagged_emails_repository._storage_repository == storage_repository

    def get_tagged_pending_emails_test(self, new_tagged_emails_repository):
        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository
        new_tagged_emails_repository._storage_repository.find_all.return_value = []

        result = new_tagged_emails_repository.get_tagged_pending_emails()
        assert result == []

    def emails_are_properly_retrieved_test(self, new_tagged_emails_repository):
        # Given
        storage_repository = Mock(StorageRepository)

        email_id = hash("any_id")
        legacy_email_tag = AnyLegacyRedisEmailTag(email_id=email_id)
        storage_repository.find_all = given("tag_email_*").returns([legacy_email_tag.dict()])

        parent_id = hash("any_parent_id")
        legacy_email = AnyLegacyRedisEmail(email_id=email_id, parent_id=parent_id)
        storage_repository.get = given(f"archived_email_{email_id}").returns({"email": legacy_email.dict()})

        parent_email = AnyRedisEmail(id=parent_id)
        parent_email_storage = Mock(RepairParentEmailStorage)
        parent_email_storage.find = given(str(parent_id)).returns(parent_email)

        new_tagged_emails_repository._storage_repository = storage_repository
        new_tagged_emails_repository._parent_email_storage = parent_email_storage

        # When
        result = new_tagged_emails_repository.get_tagged_pending_emails()

        # Then
        assert result[0].id == str(email_id)
        assert result[0].parent.id == str(parent_id)

    def get_email_details_test(self, new_tagged_emails_repository):
        email_id = 1234
        key = f"archived_email_{email_id}"
        expected_result = {"email_id": email_id, "tag": 1234}

        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository
        new_tagged_emails_repository._storage_repository.get.return_value = expected_result

        result = new_tagged_emails_repository.get_email_details(email_id)

        assert result == expected_result
        storage_repository.get.assert_called_once_with(key)

    def mark_complete_test(self, new_tagged_emails_repository):
        email_id = 1234
        tag_key = f"tag_email_{email_id}"

        archive_key = f"archived_email_{email_id}"
        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository

        new_tagged_emails_repository.mark_complete(email_id)

        storage_repository.remove.assert_called_once_with(tag_key, archive_key)

    def mark_complete_test(self, new_tagged_emails_repository):
        email_id = 1234
        tag_key = f"tag_email_{email_id}"

        archive_key = f"archived_email_{email_id}"
        storage_repository = Mock()
        new_tagged_emails_repository._storage_repository = storage_repository

        new_tagged_emails_repository.mark_complete(email_id)

        storage_repository.remove.assert_called_once_with(tag_key, archive_key)

    @patch("framework.storage.model.email_storage.datetime")
    def emails_are_properly_serialized_test(self, datetime_mock):
        datetime_mock.utcnow.return_value = "any_utcnow"
        any_date = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)

        email = Email(
            id="any_id",
            client_id="any_client_id",
            date=any_date,
            subject="any_subject",
            body="any_body",
            sender_address="any_sender_address",
            recipient_addresses=["any_recipient_address"],
            cc_addresses=["any_cc_address"],
            parent=AnyEmail(id="any_parent_id"),
            tag=EmailTag(type="any_type", probability=1.0),
        )

        serialized_email = RedisEmail(
            id="any_id",
            client_id="any_client_id",
            parent_id="any_parent_id",
            date=any_date,
            subject="any_subject",
            body="any_body",
            sender_address="any_sender_address",
            recipient_addresses=["any_recipient_address"],
            cc_addresses=["any_cc_address"],
            tag=RedisEmailTag(type="any_type", probability=1.0),
        )

        assert NewTaggedEmailsRepository.serialize_email(email) == serialized_email

    def emails_are_properly_deserialized_test(self):
        any_date = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)

        serialized_email = RedisEmail(
            id="any_id",
            client_id="any_client_id",
            date=any_date,
            subject="any_subject",
            body="any_body",
            sender_address="any_sender_address",
            recipient_addresses=["any_recipient_address"],
            cc_addresses=["any_cc_address"],
            parent_id="any_parent_id",
            tag=RedisEmailTag(type="any_type", probability=1.0),
        )

        email = Email(
            id="any_id",
            client_id="any_client_id",
            date=any_date,
            subject="any_subject",
            body="any_body",
            sender_address="any_sender_address",
            recipient_addresses=["any_recipient_address"],
            cc_addresses=["any_cc_address"],
            tag=EmailTag(type="any_type", probability=1.0),
        )

        assert NewTaggedEmailsRepository.deserialize_email(serialized_email) == email

    @patch("framework.storage.model.email_storage.datetime")
    def legacy_emails_are_properly_mapped_test(self, datetime_mock):
        datetime_mock.utcnow.return_value = "any_utcnow"

        legacy_email = LegacyRedisEmail(
            email_id=hash("any_id"),
            client_id=hash("any_client_id"),
            date="2000-1-1T00:00:00+00:00",
            subject="any_subject",
            body="any_body",
            parent_id=hash("any_parent_id"),
            from_address="any_from_address",
            to_address=["any_to_address"],
            send_cc=["any_cc_address"],
        )

        legacy_email_tag = LegacyRedisEmailTag(
            email_id=hash("any_id"),
            tag_id=hash("any_tag_id"),
            tag_probability=1.0,
        )

        redis_email = RedisEmail(
            id=str(hash("any_id")),
            client_id=str(hash("any_client_id")),
            date=datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            subject="any_subject",
            body="any_body",
            parent_id=str(hash("any_parent_id")),
            sender_address="any_from_address",
            recipient_addresses=["any_to_address"],
            cc_addresses=["any_cc_address"],
            tag=RedisEmailTag(type=str(hash("any_tag_id")), probability=1.0),
        )

        assert NewTaggedEmailsRepository.map_legacy_email(legacy_email, legacy_email_tag) == redis_email


class AnyRedisEmailTag(RedisEmailTag):
    type = "any_type"
    probability = 1.0


class AnyRedisEmail(RedisEmail):
    id = "any_id"
    client_id = "any_client_id"
    date = datetime.now(timezone.utc)
    subject = "any_subject"
    body = "any_body"
    sender_address = "any_sender_address"
    recipient_addresses: List[str] = Field(default_factory=lambda: ["any_recipient_address"])
    cc_addresses: List[str] = Field(default_factory=lambda: ["any_cc_address"])
    parent_id = "any_parent_id"
    previous_id = "any_previous_id"
    tag: RedisEmailTag = Field(default_factory=AnyRedisEmailTag)


class AnyLegacyRedisEmail(LegacyRedisEmail):
    email_id: int = hash("any_email_id")
    client_id: int = hash("any_client_id")
    parent_id: int = hash("any_parent_id")
    date: str = "2000-01-01T00:00:00+00:00"
    subject: str = "any_subject"
    body: str = "any_body"
    from_address: str = "any_from_address"
    to_address: List[str] = ["any_to_address"]
    send_cc: List[str] = ["any_cc_address"]


class AnyLegacyRedisEmailTag(LegacyRedisEmailTag):
    email_id: int = hash("any_email_id")
    tag_id: int = hash("any_tag_id")
    tag_probability: float = hash("any_tag_probability")
