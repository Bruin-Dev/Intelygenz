from typing import List

from pydantic import BaseModel, Field


class CallType(BaseModel):
    callType: str = "REP"
    category: str = "VOO"


class TicketTopics(BaseModel):
    callTypes: List[CallType] = Field(default_factory=list)
