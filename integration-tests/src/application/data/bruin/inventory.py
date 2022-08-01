from typing import List

from pydantic import BaseModel, Field


class Document(BaseModel):
    # active status
    status: str = "A"
    clientID: int = 47104
    clientName: str = "Intelygenz test"
    serviceNumber: str = "VC05200011984"
    siteID: int = 270020


class Inventory(BaseModel):
    documents: List[Document] = Field(default_factory=list)
