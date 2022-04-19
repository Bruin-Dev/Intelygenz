from typing import List

from dataclasses import dataclass, field


@dataclass
class TicketOutput:
    """
    Generic data structure to hold information on actions taken on a ticket
    """
    site_id: str = None
    ticket_id: str = None
    ticket_status: str = None
    reason: str = None
    category: str = None
    call_type: str = None
    service_numbers: List[str] = field(default_factory=list)
