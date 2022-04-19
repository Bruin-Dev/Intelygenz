from typing import List

from dataclasses import dataclass, field

from application.domain.ticket_output import TicketOutput


@dataclass
class CreateTicketsOutput:
    """
    Data structure that holds the result of creating tickets
    """
    tickets_created: List[TicketOutput] = field(default_factory=list)
    tickets_updated: List[TicketOutput] = field(default_factory=list)
    tickets_cannot_be_created: List[TicketOutput] = field(default_factory=list)
