from typing import List

from dataclasses import dataclass, field

from application.domain.topic import Topic


@dataclass
class Device:
    """
    Data structure that represents a Bruin device.
    """
    service_number: str
    client_id: int

    allowed_topics: List[Topic] = field(default_factory=list)
