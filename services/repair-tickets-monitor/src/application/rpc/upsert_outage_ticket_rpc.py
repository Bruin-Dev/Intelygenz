import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Set

from pydantic import BaseModel, Field

from application.domain.asset import AssetId
from application.rpc import Rpc, RpcError, RpcFailedError, RpcRequest

log = logging.getLogger(__name__)

NATS_TOPIC = "bruin.ticket.creation.outage.request"
BRUIN_UPDATED_STATUS = [409, 471, 472, 473]

MULTIPLE_SITES_MSG = "Multiple site ids found"
MULTIPLE_CLIENTS_MSG = "Multiple client ids found"


@dataclass
class UpsertOutageTicketRpc(Rpc):
    _topic: str = field(init=False, default=NATS_TOPIC)

    async def __call__(self, asset_ids: List[AssetId], contact_email: str) -> "UpsertedTicket":
        log.debug(f"__call__(asset_ids={asset_ids}, contact_email=**)")

        if len({asset_id.site_id for asset_id in asset_ids}) > 1:
            raise RpcError(MULTIPLE_SITES_MSG)

        client_ids = {asset_id.client_id for asset_id in asset_ids}
        if len(client_ids) > 1:
            raise RpcError(MULTIPLE_CLIENTS_MSG)

        client_id = client_ids.pop()
        service_numbers = {asset_id.service_number for asset_id in asset_ids}
        request = RpcRequest(
            body=RequestBody(
                client_id=client_id,
                # There is no typo here, the NATS API expects a service_number parameter
                service_number=service_numbers,
                ticket_contact=TicketContact(email=contact_email),
            )
        )

        try:
            response = await self.send(request)
            status = UpsertedStatus.created
        except RpcFailedError as error:
            if error.response.status in BRUIN_UPDATED_STATUS:
                response = error.response
                status = UpsertedStatus.updated
            else:
                raise error

        try:
            ticket_id = str(int(response.body))
        except (ValueError, TypeError) as error:
            raise RpcFailedError(request=request, response=response) from error

        return UpsertedTicket(ticket_id=ticket_id, status=status)


class TicketContact(BaseModel):
    email: str = Field(repr=False)


class RequestBody(BaseModel):
    client_id: str
    service_number: Set[str]
    ticket_contact: TicketContact


class UpsertedStatus(Enum):
    created = auto()
    updated = auto()


class UpsertedTicket(BaseModel):
    status: UpsertedStatus
    ticket_id: str
