from typing import List

from pydantic import BaseModel, Field


class TicketDetail(BaseModel):
    pass


class TicketNote(BaseModel):
    serviceNumber: List[str] = Field(default_factory=list)


class TicketDetails(BaseModel):
    ticketDetails: List[TicketDetail] = Field(default_factory=list)
    ticketNotes: List[TicketNote] = Field(default_factory=list)
