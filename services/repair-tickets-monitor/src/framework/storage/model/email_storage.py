from datetime import datetime
from typing import List, Optional, Type

from dataclasses import dataclass
from framework.storage.model.model_storage import ModelStorage
from pydantic import BaseModel, Field


class EmailMetadata(BaseModel):
    # Internal datetimes need no timezone, but should remain utc datetimes
    utc_creation_datetime: datetime = Field(default_factory=datetime.utcnow)


class EmailTag(BaseModel):
    type: int
    probability: float


class Email(BaseModel):
    email_id: int
    client_id: int
    date: str
    subject: str
    body: str
    from_address: str
    to_address: List[str]
    send_cc: List[str]
    parent_id: Optional[int]
    previous_id: Optional[int]
    tag: Optional[EmailTag]
    metadata: EmailMetadata = Field(default_factory=EmailMetadata)


@dataclass
class EmailStorage(ModelStorage[Email]):
    data_type: Type = Email


@dataclass
class RepairParentEmailStorage(EmailStorage):
    data_name: str = "parent-email:repair"


@dataclass
class RepairReplyEmailStorage(EmailStorage):
    data_name: str = "reply-email:repair"
