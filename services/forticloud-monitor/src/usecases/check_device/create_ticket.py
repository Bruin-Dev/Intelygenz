import logging
from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError, root_validator

from clients.http_client import HttpClient, HttpRequest
from shared.errors import UnexpectedResponseError, UnexpectedStatusError

from .device import DeviceId
from .ticket import CreatedTicket

log = logging.getLogger(__name__)

STATUS_DESCRIPTIONS = {
    409: "There is already an existing In-Progress ticket for those service numbers.",
    471: "There is already an existing Resolved ticket for those service numbers but couldn't be set to In-Progress.",
    472: "There is already an existing Resolved ticket for those service numbers and has been set to In-Progress.",
    473: "There is already an existing Resolved ticket at the service numbers location. "
    "It has been set to In-Progress and a ticket detail has been added for the provided service numbers.",
}

DESCRIPTION = "MetTel's IPA -- Service Outage Trouble"


@dataclass
class CreateTicket:
    http_client: HttpClient

    async def __call__(self, device_id: DeviceId) -> CreatedTicket:
        log.debug(f"(device={device_id})")
        request_body = RequestBody.build_for(device_id, DESCRIPTION)
        request = PostOutageTicket(request_body.dict())
        response = await self.http_client.send(request)
        log.debug(f"http_client.send({request})={response}")
        if not response.is_ok:
            raise UnexpectedStatusError(response.status)

        try:
            response_body = ResponseBody.parse_raw(response.body)
        except ValidationError as e:
            raise UnexpectedResponseError from e

        first_item = response_body.first_item
        status_description = STATUS_DESCRIPTIONS.get(first_item.errorCode)
        return CreatedTicket(ticket_id=str(first_item.ticketId), status_description=status_description)


@dataclass
class PostOutageTicket(HttpRequest):
    method: str = "POST"
    path: str = "/api/Ticket/repair"


class RequestBody(BaseModel):
    ClientID: int
    WTNs: List[str]
    RequestDescription: str

    @classmethod
    def build_for(cls, device_id: DeviceId, description: str):
        return cls(ClientID=device_id.client_id, WTNs=[device_id.service_number], RequestDescription=description)


class Item(BaseModel):
    ticketId: int
    errorCode: Optional[int]


class ResponseBody(BaseModel):
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
