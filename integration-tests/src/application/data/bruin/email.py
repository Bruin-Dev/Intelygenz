import datetime
import time
from typing import List, Optional

from pydantic import BaseModel, Field
from shortuuid import uuid


class TicketModel(BaseModel):
    TicketId: str = "1432293840"


class BodyModel(BaseModel):
    EmailId: int = Field(default_factory=lambda: round(time.time() * 1000))
    ClientId: int = 47104
    Subject: str = "CENTER 1085 Multiple Computers - Internet Outage - Network / Internet"
    Date: str = Field(
        default_factory=lambda: datetime.datetime.utcnow()
        .replace(microsecond=0, tzinfo=datetime.timezone.utc)
        .isoformat()
    )
    Body: str = ""
    TagID: List[int] = Field(default_factory=list)
    FromAddress: str = "help1@calibercollision.com"
    ToAddress: List[str] = Field(default_factory=lambda: ["caliber@mettel.net"])
    SendCC: List[str] = Field(default_factory=list)
    ParentId: Optional[int] = None
    Ticket: Optional[TicketModel] = None


class NotificationModel(BaseModel):
    Id: str = Field(default_factory=uuid)
    ClientId: int = 47104
    EntityId: str = "4104172"
    ApplicationName: str = "EmailCenter"
    Action: str = "EmailReceived"
    Body: BodyModel = Field(default_factory=lambda: BodyModel())


class Email(BaseModel):
    Id: str = Field(default_factory=uuid)
    Attempt: int = 1
    Notification: NotificationModel = Field(default_factory=lambda: NotificationModel())
