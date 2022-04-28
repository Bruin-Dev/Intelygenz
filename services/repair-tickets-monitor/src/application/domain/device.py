from dataclasses import dataclass


@dataclass
class Device:
    """
    Data structure that represents a Bruin device.
    """
    service_number: str
    client_id: int
