from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import List, Optional


@dataclass
class EmailTag:
    type: str
    probability: float


@dataclass
class Email:
    id: str
    client_id: str
    date: str
    subject: str
    body: str
    tag: EmailTag
    sender_address: str
    recipient_addresses: List[str] = field(default_factory=list)
    cc_addresses: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    previous_id: Optional[str] = None

    def comma_separated_cc_addresses(self) -> str:
        return ", ".join(self.cc_addresses) if self.cc_addresses else ""


class EmailStatus(IntEnum):
    NEW = auto()
    AIQ = auto()
    DONE = auto()
