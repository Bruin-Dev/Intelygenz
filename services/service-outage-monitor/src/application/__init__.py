from enum import Enum, auto


class Outages(Enum):
    LINK_DOWN = 'Link Down Outage (no HA)'
    HARD_DOWN = 'Hard Down Outage (no HA)'

    HA_LINK_DOWN = 'Link Down Outage (HA)'
    HA_SOFT_DOWN = 'Soft Down Outage (HA)'
    HA_HARD_DOWN = 'Hard Down Outage (HA)'


class ForwardQueues(Enum):
    ASR = 'ASR Investigate'
    HNOC = 'HNOC Investigate'
    WIRELESS = 'Wireless Repair Intervention Needed'


class ChangeTicketSeverityStatus(Enum):
    CHANGED_TO_LINK_DOWN_SEVERITY = auto()
    CHANGED_TO_EDGE_DOWN_SEVERITY = auto()
    NOT_CHANGED = auto()
