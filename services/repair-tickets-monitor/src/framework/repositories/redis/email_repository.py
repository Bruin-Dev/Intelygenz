from typing import List, Optional, Type

from dataclasses import dataclass
from framework.repositories.redis.redis_repository import RedisRepository
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
    tag: EmailTag


@dataclass
class EmailRepository(RedisRepository[Email]):
    model_type: Type = Email


@dataclass
class RepairParentEmailRepository(EmailRepository):
    model_name: str = "parent-email:repair"


@dataclass
class RepairReplyEmailRepository(EmailRepository):
    model_name: str = "reply-email:repair"
