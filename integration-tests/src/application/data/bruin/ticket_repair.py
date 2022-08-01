from typing import List

from pydantic import BaseModel, Field


class Item(BaseModel):
    ticketId: int = 4767771
    errorCode: int = 200


class TicketRepair(BaseModel):
    items: List[Item] = Field(default_factory=list)
