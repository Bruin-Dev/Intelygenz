from datetime import datetime, timezone
from typing import List, Optional, Type

from dataclasses import dataclass
from framework.storage.model.model_storage import ModelStorage
from pydantic import BaseModel


class EmailMetadata(BaseModel):
    utc_creation_datetime: datetime = datetime.now(timezone.utc)


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
    metadata: EmailMetadata = EmailMetadata()


@dataclass
class EmailStorage(ModelStorage[Email]):
    data_type: Type = Email


@dataclass
class RepairParentEmailStorage(EmailStorage):
    data_name: str = "parent-email:repair"


@dataclass
class RepairReplyEmailStorage(EmailStorage):
    data_name: str = "reply-email:repair"
