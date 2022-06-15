import datetime
import time

from pydantic import BaseModel
from shortuuid import uuid


class Body(BaseModel):
    EmailId = round(time.time() * 1000)
    ClientId = 30000
    Subject = "CENTER 1085 Multiple Computers - Internet Outage - Network / Internet"
    Date = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc).isoformat()
    Body = ""
    TagID = []
    FromAddress = "help1@calibercollision.com"
    ToAddress = ["caliber@mettel.net"]
    SendCC = []


class Notification(BaseModel):
    Id = uuid()
    ClientId = 30000
    EntityId = "4104172"
    ApplicationName = "EmailCenter"
    Action = "EmailReceived"
    Body = Body()


class Email(BaseModel):
    Id = uuid()
    Attempt = 1
    Notification = Notification()
