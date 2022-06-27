from typing import List, Optional

from dataclasses import dataclass, field


@dataclass
class EmailTag:
    type: int
    probability: float


@dataclass
class Email:
    email_id: int
    client_id: int
    date: str
    subject: str
    body: str
    tag: EmailTag
    from_address: str
    to_address: List[str] = field(default_factory=list)
    send_cc: List[str] = field(default_factory=list)
    parent_id: Optional[int] = None
    previous_id: Optional[int] = None
