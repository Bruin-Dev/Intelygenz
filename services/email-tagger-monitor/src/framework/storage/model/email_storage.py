from datetime import datetime
from typing import List, Optional, Type

from dataclasses import dataclass
from framework.storage.model.model_storage import ModelStorage
from pydantic import BaseModel, Field


class EmailMetadata(BaseModel):
    # Internal datetimes need no timezone, but should remain utc datetimes
    # lambda was used to be able to properly mock datetime @ unit tests
    utc_creation_datetime: datetime = Field(default_factory=lambda: datetime.utcnow())


class EmailTag(BaseModel):
    type: str
    probability: float


class Email(BaseModel):
    id: str
    client_id: str
    date: datetime
    subject: str
    body: str
    sender_address: str
    recipient_addresses: List[str]
    cc_addresses: List[str]
    parent_id: Optional[str]
    previous_id: Optional[str]
    tag: EmailTag
    metadata: EmailMetadata = Field(default_factory=EmailMetadata)


@dataclass
class EmailStorage(ModelStorage[Email]):
    data_type: Type = Email

    def store(self, email: Email, ttl_seconds: Optional[int] = None) -> bool:
        return super().set(email.id, email, ttl_seconds)

    def delete(self, email: Email) -> int:
        return super().delete(email.id)


@dataclass
class RepairParentEmailStorage(EmailStorage):
    data_name: str = "parent-email:repair"


@dataclass
class RepairReplyEmailStorage(EmailStorage):
    data_name: str = "reply-email:repair"
