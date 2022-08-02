from dataclasses import dataclass, field
from typing import Dict, List

from multipledispatch import dispatch

from application.domain.ticket import Ticket


@dataclass
class CreateTicketsOutput:
    """
    Data structure that holds the result of creating tickets
    """

    tickets_created: List["TicketOutput"] = field(default_factory=list)
    tickets_updated: List["TicketOutput"] = field(default_factory=list)
    tickets_cannot_be_created: List["TicketOutput"] = field(default_factory=list)


@dataclass
class PotentialTicketsOutput:
    """
    Data structure that holds potential actions that could have been taken
    """

    tickets_could_be_created: List["TicketOutput"] = field(default_factory=list)
    tickets_could_be_updated: List["TicketOutput"] = field(default_factory=list)


@dataclass
class RepairEmailOutput:
    """
    Data structure that holds information to be returned to KRE as feedback
    """

    email_id: int
    service_numbers_sites_map: Dict[str, str] = field(default_factory=dict)
    validated_tickets: List[Ticket] = field(default_factory=list)
    tickets_created: List["TicketOutput"] = field(default_factory=list)
    tickets_updated: List["TicketOutput"] = field(default_factory=list)
    tickets_could_be_created: List["TicketOutput"] = field(default_factory=list)
    tickets_could_be_updated: List["TicketOutput"] = field(default_factory=list)
    tickets_cannot_be_created: List["TicketOutput"] = field(default_factory=list)

    @dispatch(CreateTicketsOutput)
    def extend(self, create_tickets_output: CreateTicketsOutput):
        self.tickets_created.extend(create_tickets_output.tickets_created)
        self.tickets_updated.extend(create_tickets_output.tickets_updated)
        self.tickets_cannot_be_created.extend(create_tickets_output.tickets_cannot_be_created)

    @dispatch(PotentialTicketsOutput)
    def extend(self, potential_tickets_output: PotentialTicketsOutput):
        self.tickets_could_be_created.extend(potential_tickets_output.tickets_could_be_created)
        self.tickets_could_be_updated.extend(potential_tickets_output.tickets_could_be_updated)


@dataclass
class TicketOutput:
    """
    Generic data structure to hold information on actions taken on a ticket
    """

    site_id: str = None
    ticket_id: str = None
    reason: str = None
    service_numbers: List[str] = field(default_factory=list)
