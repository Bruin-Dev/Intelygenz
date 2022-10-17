from dataclasses import dataclass


@dataclass
class Note:
    ticket_id: str
    service_number: str
    text: str
