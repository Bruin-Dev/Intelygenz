from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Response(BaseModel):
    clientID: int = 47104
    ticketID: int = 4767771
    ticketStatus: str = "InProgress"
    callType: str = "REP"
    category: str = "VOO"
    createDate: str = Field(default_factory=lambda: str(datetime.now()))
    createdBy: str = "Intelygenz AI"


class TicketBasic(BaseModel):
    total: int = 0
    start: int = 0
    currentPageSize: int = 10
    responses: List[Response] = Field(default_factory=list)
