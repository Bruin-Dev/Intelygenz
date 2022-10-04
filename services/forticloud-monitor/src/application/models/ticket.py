from dataclasses import dataclass
from enum import IntEnum


class TicketStatus(IntEnum):
    CREATED = 200
    IN_PROGRESS = 409
    FAILED_REOPENING = 471
    REOPENED = 472
    REOPENED_SAME_LOCATION = 473


@dataclass
class CreatedTicket:
    ticket_id: str
    ticket_status: TicketStatus
