import asyncio
import logging
from dataclasses import dataclass, field
from datetime import timedelta
from http import HTTPStatus
from typing import List, Optional

from bruin_client import BruinClient, BruinRequest, BruinResponse
from pydantic import ValidationError

from application.domain.device import DeviceId
from application.domain.note import Note
from application.domain.task import TicketTask
from application.domain.ticket import CreatedTicket, Ticket, TicketStatus
from application.repositories.bruin_repository_models.find_ticket import (
    BruinTicket,
    BruinTicketData,
    BruinTicketsResponse,
    FindTicketQuery,
)
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

OPEN_TICKET_STATUS = ["New", "InProgress", "Draft"]


@dataclass
class TaskSettings:
    auto_resolution_grace_period: timedelta
    max_auto_resolutions: int


@dataclass
class BruinRepository:
    bruin_client: BruinClient = field(repr=False)
    task_settings: TaskSettings

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

    async def find_ticket(self, query: FindTicketQuery) -> Optional[Ticket]:
        log.debug(f"find_ticket(query={query})")

        bruin_tickets = await self._find_bruin_tickets(query)
        candidate_ticket = self._find_candidate_ticket(query, bruin_tickets)
        if not candidate_ticket:
            return None

        ticket_data = await self._find_ticket_data(candidate_ticket.ticketID)
        if not ticket_data:
            return None

        return self._build_ticket(candidate_ticket, ticket_data)

    async def _find_bruin_tickets(self, query: FindTicketQuery) -> List[BruinTicket]:
        log.debug(f"_find_bruin_tickets()")

        # Build the queries, a query for each ticket status
        requests = []
        for status in query.statuses:
            query_params = query.params_with(status=status)
            request = BruinRequest(method="GET", path=f"/api/Ticket/basic", query_params=query_params)
            requests.append(self.bruin_client.send(request))
            log.debug(f"_find_bruin_tickets(): request={request}")

        # Run all the queries
        responses = await asyncio.gather(*requests, return_exceptions=True)
        log.debug(f"_find_bruin_tickets(): responses={responses}")

        # Save the queries that did ok and log the ones that didn't
        bruin_responses = []
        for index, response in enumerate(responses):
            if isinstance(response, BruinResponse) and response.status == HTTPStatus.OK:
                bruin_responses.append(response)
            else:
                log.warning(f"Couldn't get {query.statuses[index]} status tickets: response={response}")

        # Parse the responses and return the bruin tickets
        bruin_tickets = []
        for bruin_response in bruin_responses:
            try:
                bruin_ticket_response = BruinTicketsResponse.parse_raw(bruin_response.text)
                bruin_tickets += bruin_ticket_response.responses
            except ValidationError as e:
                log.warning(f"Couldn't deserialize response={bruin_response.text}: {e}")

        return bruin_tickets

    def _find_candidate_ticket(self, query: FindTicketQuery, bruin_tickets: List[BruinTicket]) -> Optional[BruinTicket]:
        log.debug(f"_find_candidate_ticket(bruin_tickets={bruin_tickets}")

        # There should be just a single ticket: we will work the first one if there are more than one.
        if len(bruin_tickets) == 0:
            return None
        elif len(bruin_tickets) > 1:
            ticket_ids = [ticket_item.ticketID for ticket_item in bruin_tickets]
            log.warning(f"Multiple tickets were found for {query.device_id}: {ticket_ids}")

        candidate_ticket = bruin_tickets[0]

        # Check if the ticket was created by the corresponding query user
        if candidate_ticket.createdBy == query.created_by:
            return candidate_ticket
        else:
            log.debug(f"Ticket was created by '{candidate_ticket.createdBy}' instead of '{query.created_by}'")
            return None

    async def _find_ticket_data(self, ticket_id: int) -> Optional[BruinTicketData]:
        log.debug(f"_find_ticket_data(ticket_id={ticket_id})")

        request = BruinRequest(method="GET", path=f"/api/Ticket/{ticket_id}/details")
        response = await self.bruin_client.send(request)
        log.debug(f"bruin_client.send({request})={response}")
        if response.status != HTTPStatus.OK:
            log.warning(f"Couldn't get ticket {ticket_id} data: {response}")
            return None

        return BruinTicketData.parse_raw(response.text)

    def _build_ticket(self, candidate_ticket: "BruinTicket", ticket_data: "BruinTicketData") -> Ticket:
        log.debug(f"_build_ticket(candidate_ticket={candidate_ticket}, ticket_data={ticket_data})")
        ticket_tasks = ticket_data.build_ticket_tasks_with(
            task_auto_resolution_grace_period=self.task_settings.auto_resolution_grace_period,
            task_max_auto_resolutions=self.task_settings.max_auto_resolutions,
        )
        return Ticket(id=str(candidate_ticket.ticketID), created_at=candidate_ticket.createDate, tasks=ticket_tasks)

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
