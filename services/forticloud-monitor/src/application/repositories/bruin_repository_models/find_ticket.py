import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from dateutil.parser import parse
from pydantic import BaseModel, Field, validator

from application.domain.device import DeviceId
from application.domain.service_number import ServiceNumber
from application.domain.task import (
    AUTO_RESOLUTION_HEADER,
    REOPEN_HEADER,
    TRIAGE_HEADER,
    TaskCycle,
    TaskCycleStatus,
    TicketTask,
)

log = logging.getLogger(__name__)


@dataclass
class FindTicketQuery:
    created_by: str
    ticket_topic: str
    device_id: DeviceId
    statuses: List[str]

    def params_with(self, status: str):
        return {
            "TicketStatus": status,
            "TicketTopic": self.ticket_topic,
            "ClientId": self.device_id.client_id,
            "ServiceNumber": self.device_id.service_number,
        }


#
# Bruin response models
#


class BruinTicket(BaseModel):
    ticketID: int
    createdBy: str
    createDate: datetime

    @validator("createDate", pre=True)
    def validate_date(cls, value):
        if isinstance(value, datetime):
            return value
        else:
            return parse(value).replace(tzinfo=timezone.utc)


class BruinTicketsResponse(BaseModel):
    responses: List[BruinTicket] = Field(default_factory=list)

    @validator("responses", pre=True)
    def validate_responses(cls, value):
        assert isinstance(value, list)

        responses = []
        for item in value:
            try:
                responses.append(BruinTicket.parse_obj(item))
            except Exception as e:
                log.warning(f"Couldn't parse BruinTicket={item}: {e}")
                pass

        return responses


class BruinTicketDetail(BaseModel):
    detailID: int
    detailValue: str
    detailStatus: str

    @property
    def is_resolved(self):
        return self.detailStatus == "R"


class BruinTicketNote(BaseModel):
    noteValue: str
    createdDate: datetime
    serviceNumber: List[str]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.createdDate = self.createdDate.astimezone(timezone.utc)

    @property
    def is_triage_note(self) -> bool:
        return os.linesep.join(TRIAGE_HEADER) in self.noteValue

    @property
    def is_reopen_note(self) -> bool:
        return os.linesep.join(REOPEN_HEADER) in self.noteValue

    @property
    def is_auto_resolution_note(self) -> bool:
        return os.linesep.join(AUTO_RESOLUTION_HEADER) in self.noteValue

    @property
    def is_cycle_note(self) -> bool:
        return self.is_triage_note or self.is_reopen_note or self.is_auto_resolution_note


class BruinTicketData(BaseModel):
    ticketDetails: List[BruinTicketDetail] = Field(default_factory=list)
    ticketNotes: List[BruinTicketNote] = Field(default_factory=list)

    @validator("ticketDetails", pre=True)
    def validate_ticket_details(cls, value):
        assert isinstance(value, list)

        ticket_details = []
        for item in value:
            try:
                ticket_details.append(BruinTicketDetail.parse_obj(item))
            except Exception as e:
                log.warning(f"Couldn't parse BruinTicketDetail={item}: {e}")
                pass

        return ticket_details

    @validator("ticketNotes", pre=True)
    def validate_ticket_notes(cls, value):
        assert isinstance(value, list)

        ticket_notes = []
        for item in value:
            try:
                ticket_notes.append(BruinTicketNote.parse_obj(item))
            except Exception as e:
                log.warning(f"Couldn't parse BruinTicketDetail={item}: {e}")
                pass

        return ticket_notes

    def build_ticket_tasks_with(
        self,
        task_auto_resolution_grace_period: timedelta,
        task_max_auto_resolutions: int,
    ) -> Dict[ServiceNumber, TicketTask]:
        ticket_tasks = {}
        for ticket_detail in self.ticketDetails:
            # extract and sort the corresponding task notes
            task_notes = [
                ticket_note
                for ticket_note in self.ticketNotes
                if ticket_detail.detailValue in ticket_note.serviceNumber
            ]
            # Sort chronologically the notes (oldest ones first)
            sorted_task_notes = sorted(task_notes, key=lambda item: item.created_at)
            log.debug(f"BruinTicketData:sorted_task_notes={sorted_task_notes}")

            # Build the list of task cycles
            # If everything went ok, we should have an even list of (triage|re-open)/auto-resolved note pairs
            # If that's not the case, this loop will:
            # - admit solitary auto-resolved notes as an AUTORESOLVED cycle
            # - admit any number of triage or re-open notes before an auto-resolved note to form an AUTORESOLVED cycle
            task_cycles = []
            current_cycle_datetime = None
            for task_note in sorted_task_notes:
                if not current_cycle_datetime and task_note.is_cycle_note:
                    current_cycle_datetime = task_note.createdDate
                if task_note.is_auto_resolution_note:
                    current_cycle = TaskCycle(created_at=current_cycle_datetime, status=TaskCycleStatus.AUTO_RESOLVED)
                    task_cycles.append(current_cycle)
                    current_cycle_datetime = None

            # If there's any current cycle after going through the loop, it has to be an ONGOING cycle
            if current_cycle_datetime:
                current_cycle = TaskCycle(created_at=current_cycle_datetime, status=TaskCycleStatus.ONGOING)
                task_cycles.append(current_cycle)

            log.debug(f"BruinTicketData:task_cycles={task_cycles}")

            service_number = ServiceNumber(ticket_detail.detailValue)
            ticket_task = TicketTask(
                id=str(ticket_detail.detailID),
                service_number=service_number,
                auto_resolution_grace_period=task_auto_resolution_grace_period,
                max_auto_resolutions=task_max_auto_resolutions,
                is_resolved=ticket_detail.is_resolved,
                cycles=task_cycles,
            )

            ticket_tasks[service_number] = ticket_task

        log.debug(f"BruinTicketData:ticket_tasks={ticket_tasks}")
        return ticket_tasks
