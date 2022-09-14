from dataclasses import dataclass


@dataclass
class Ticket:
    client_id: str
    service_number: str
