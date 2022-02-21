import re
from enum import Enum


class AffectingTroubles(Enum):
    LATENCY = 'Latency'
    PACKET_LOSS = 'Packet Loss'
    JITTER = 'Jitter'
    BANDWIDTH_OVER_UTILIZATION = 'Bandwidth Over Utilization'
    BOUNCING = 'Circuit Instability'


EVENT_INTERFACE_REGEX = re.compile(
    r'(^Interface (?P<interface>[a-zA-Z0-9]+) is (up|down)$)|'
    r'(^Link (?P<link_interface>[a-zA-Z0-9]+) is (no longer|now) DEAD$)'
)
