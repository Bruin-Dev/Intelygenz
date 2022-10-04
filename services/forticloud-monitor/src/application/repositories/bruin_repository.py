import logging
from dataclasses import dataclass, field
from http import HTTPStatus

from bruin_client import BruinClient, BruinRequest
from pydantic import ValidationError

from application.models.device import DeviceId
from application.models.note import Note
from application.models.ticket import CreatedTicket, TicketStatus
from application.repositories.bruin_repository_models.post_repair_ticket import (
    PostRepairTicketBody,
    PostRepairTicketResponse,
)
from application.repositories.bruin_repository_models.post_ticket_note import PostTicketNoteBody
from application.repositories.errors import UnexpectedResponseError, UnexpectedStatusError

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
class BruinRepository:
    bruin_client: BruinClient = field(repr=False)

    async def post_repair_ticket(self, device_id: DeviceId) -> CreatedTicket:
        log.debug(f"post_repair_ticket(device={device_id})")
        request_body = PostRepairTicketBody.build_for(device_id, DESCRIPTION)
        request = BruinRequest(method="POST", path="/api/Ticket/repair", json=request_body.json())
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")

        if not response.status == HTTPStatus.OK:
            raise UnexpectedStatusError(response.status)

        try:
            response_body = PostRepairTicketResponse.parse_raw(response.text)
        except ValidationError as e:
            raise UnexpectedResponseError from e

        first_item = response_body.first_item
        ticket_status = TicketStatus.CREATED
        if first_item.errorCode in list(TicketStatus):
            ticket_status = TicketStatus(first_item.errorCode)

        return CreatedTicket(ticket_id=str(first_item.ticketId), ticket_status=ticket_status)

    async def post_ticket_note(self, note: Note):
        log.debug(f"post_ticket_note(note={note})")
        request_body = PostTicketNoteBody(
            note=note.text,
            serviceNumbers=[note.service_number],
        )
        request = BruinRequest(
            method="POST",
            path=f"/api/Ticket/{note.ticket_id}/notes",
            json=request_body.json(),
        )
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")

        if not response.status == HTTPStatus.OK:
            raise UnexpectedStatusError(response.status)
