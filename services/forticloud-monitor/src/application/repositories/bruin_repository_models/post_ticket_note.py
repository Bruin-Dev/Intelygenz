from typing import List

from pydantic.main import BaseModel


class PostTicketNoteBody(BaseModel):
    note: str
    serviceNumbers: List[str]
