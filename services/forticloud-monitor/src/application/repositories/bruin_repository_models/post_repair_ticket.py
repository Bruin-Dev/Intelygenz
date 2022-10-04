from dataclasses import dataclass
from typing import List, Optional

from bruin_client import BruinRequest
from pydantic import Field, root_validator
from pydantic.main import BaseModel

from application.models.device import DeviceId


@dataclass
class PostRepairTicket(BruinRequest):
    method: str = "POST"
    path: str = "/api/Ticket/repair"


class PostRepairTicketBody(BaseModel):
    ClientID: int
    WTNs: List[str]
    RequestDescription: str

    @classmethod
    def build_for(cls, device_id: DeviceId, description: str):
        return cls(ClientID=device_id.client_id, WTNs=[device_id.service_number], RequestDescription=description)


class Item(BaseModel):
    ticketId: int
    errorCode: Optional[int]


class PostRepairTicketResponse(BaseModel):
    assets: List[Item] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list)

    @root_validator
    def check_items(cls, values):
        assets = values.get("assets")
        items = values.get("items")
        assert len(assets) > 0 or len(items) > 0, "At least an asset or an item are required"
        return values

    @property
    def first_item(self) -> Optional[Item]:
        if self.assets:
            return self.assets[0]
        else:
            return self.items[0]
