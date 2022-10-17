import logging
from dataclasses import dataclass, field
from http import HTTPStatus

from bruin_client import BruinClient, BruinRequest
from pydantic import ValidationError

from application.domain.device import DeviceId
from application.domain.note import Note
from application.domain.task import TicketTask
from application.domain.ticket import CreatedTicket, Ticket, TicketStatus
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
        request = BruinRequest(method="POST", path="/api/Ticket/repair", json=request_body.dict())
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
            json=request_body.dict(),
        )
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")

        if not response.status == HTTPStatus.OK:
            raise UnexpectedStatusError(response.status)

    async def find_open_automation_ticket_for(self, device_id: DeviceId) -> Ticket:
        pass

    async def unpause_task(self, ticket_id: str, task: TicketTask):
        log.debug(f"unpause_task(ticket_id={ticket_id}, task={task})")
        request = BruinRequest(
            method="POST",
            path=f"/api/Ticket/{ticket_id}/detail/unpause",
            json={"serviceNumber": task.service_number, "detailId": int(task.id)},
        )
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")

        if not response.status == HTTPStatus.OK:
            raise UnexpectedStatusError(response.status)

    async def resolve_task(self, ticket_id: str, task: TicketTask):
        log.debug(f"resolve_task(ticket_id={ticket_id}, task={task})")
        request = BruinRequest(
            method="POST",
            path=f"/api/Ticket/{ticket_id}/details/{task.id}/status",
            json={"Status": "R"},
        )
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")

        if not response.status == HTTPStatus.OK:
            raise UnexpectedStatusError(response.status)
