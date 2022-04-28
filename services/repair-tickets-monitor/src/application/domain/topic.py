from dataclasses import dataclass


@dataclass
class Topic:
    """
    Data structure that represents a Bruin topic.
    """
    call_type: str
    category: str
