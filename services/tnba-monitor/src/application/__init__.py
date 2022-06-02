import re
from enum import Enum


class AffectingTroubles(Enum):
    LATENCY = "Latency"
    PACKET_LOSS = "Packet Loss"
    JITTER = "Jitter"
    BANDWIDTH_OVER_UTILIZATION = "Bandwidth Over Utilization"
    BOUNCING = "Circuit Instability"


TROUBLES_DISJUNCTION_FOR_REGEX = "|".join(trouble.value for trouble in AffectingTroubles)
