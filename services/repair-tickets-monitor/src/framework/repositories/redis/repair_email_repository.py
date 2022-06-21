from typing import List, Type

from dataclasses import dataclass
from framework.repositories.redis.redis_repository import RedisRepository
from pydantic import BaseModel


class RepairEmail(BaseModel):
    email_id: int
    client_id: int
    date: str
    subject: str
    body: str
    from_address: str
    to_address: List[str]
    send_cc: List[str]


@dataclass
class RepairEmailRepository(RedisRepository[RepairEmail]):
    entity_name: str = "email:repair"
    entity_type: Type = RepairEmail
