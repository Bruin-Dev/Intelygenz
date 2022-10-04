from dataclasses import dataclass


@dataclass
class ConsumerSettings:
    queue: str
    subject: str
