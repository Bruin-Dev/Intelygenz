from typing import List

from dataclasses import dataclass, field

from application.domain.ticket_output import TicketOutput


@dataclass
class PotentialTicketsOutput:
    """
    Data structure that holds potential actions that could have been taken
    """
    tickets_could_be_created: List[TicketOutput] = field(default_factory=list)
    tickets_could_be_updated: List[TicketOutput] = field(default_factory=list)
