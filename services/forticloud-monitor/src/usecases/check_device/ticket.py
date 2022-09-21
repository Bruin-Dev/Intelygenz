from dataclasses import dataclass
from typing import Optional


@dataclass
class Ticket:
    client_id: str
    service_number: str


@dataclass
class CreatedTicket:
    ticket_id: str
    status_description: Optional[str] = None
