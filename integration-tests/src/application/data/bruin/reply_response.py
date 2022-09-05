import time

from pydantic import BaseModel, Field


class ReplyResponse(BaseModel):
    emailId: int = Field(default_factory=lambda: round(time.time() * 1000))
