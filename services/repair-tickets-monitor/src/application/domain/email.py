from datetime import datetime
from enum import IntEnum, auto
from typing import List, Optional

from dataclasses import dataclass, field


@dataclass
class EmailTag:
    type: str
    probability: float


@dataclass
class Email:
    id: str
    client_id: str
    date: datetime
    subject: str
    body: str = field(repr=False)
    tag: EmailTag
    sender_address: str = field(repr=False)
    recipient_addresses: List[str] = field(default_factory=list, repr=False)
    cc_addresses: List[str] = field(default_factory=list, repr=False)
    parent: Optional["Email"] = None

    def comma_separated_cc_addresses(self) -> str:
        return ", ".join(self.cc_addresses) if self.cc_addresses else ""

    @property
    def is_parent_email(self) -> bool:
        return self.parent is None

    @property
    def is_reply_email(self) -> bool:
        return self.parent is not None

    @property
    def reply_interval(self) -> Optional[int]:
        if self.is_parent_email:
            return None

        interval = self.date - self.parent.date
        return interval.seconds


class EmailStatus(IntEnum):
    NEW = auto()
    AIQ = auto()
    DONE = auto()
