from typing import List, Dict
from multipledispatch import dispatch

from dataclasses import dataclass, field

from application.domain.create_tickets_output import CreateTicketsOutput
from application.domain.potential_tickets_output import PotentialTicketsOutput
from application.domain.ticket_output import TicketOutput


@dataclass
class RepairEmailOutput:
    """
    Data structure that holds information to be returned to KRE as feedback
    """
    email_id: str
    service_numbers_sites_map: Dict[str, str] = field(default_factory=list)
    validated_ticket_numbers: List[str] = field(default_factory=list)
    tickets_created: List[TicketOutput] = field(default_factory=list)
    tickets_updated: List[TicketOutput] = field(default_factory=list)
    tickets_could_be_created: List[TicketOutput] = field(default_factory=list)
    tickets_could_be_updated: List[TicketOutput] = field(default_factory=list)
    tickets_cannot_be_created: List[TicketOutput] = field(default_factory=list)

    @dispatch(CreateTicketsOutput)
    def extend(self, create_tickets_output: CreateTicketsOutput):
        self.tickets_created.extend(create_tickets_output.tickets_created)
        self.tickets_updated.extend(create_tickets_output.tickets_updated)
        self.tickets_cannot_be_created.extend(create_tickets_output.tickets_cannot_be_created)

    @dispatch(PotentialTicketsOutput)
    def extend(self, potential_tickets_output: PotentialTicketsOutput):
        self.tickets_could_be_created.extend(potential_tickets_output.tickets_could_be_created)
        self.tickets_could_be_updated.extend(potential_tickets_output.tickets_could_be_updated)
