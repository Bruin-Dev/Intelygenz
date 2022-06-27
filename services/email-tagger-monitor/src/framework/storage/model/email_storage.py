from typing import List, Optional, Type

from dataclasses import dataclass
from framework.storage.model.model_storage import ModelStorage
from pydantic import BaseModel


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


class TaggedEmail(Email):
    tag: EmailTag


@dataclass
class EmailStorage(ModelStorage[Email]):
    data_type: Type = Email


@dataclass
class TaggedEmailStorage(ModelStorage[TaggedEmail]):
    data_type: Type = Email


@dataclass
class RepairParentEmailStorage(TaggedEmailStorage):
    data_name: str = "parent-email:repair"


@dataclass
class RepairReplyEmailStorage(EmailStorage):
    data_name: str = "reply-email:repair"
