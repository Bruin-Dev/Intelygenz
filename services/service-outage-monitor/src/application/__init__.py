from enum import Enum, auto


class Outages(Enum):
    LINK_DOWN = 'Link Down (no HA)'
    HARD_DOWN = 'Hard Down (no HA)'

    HA_LINK_DOWN = 'Link Down (HA)'
    HA_SOFT_DOWN = 'Soft Down (HA)'
    HA_HARD_DOWN = 'Hard Down (HA)'


class ForwardQueues(Enum):
    ASR = 'ASR Investigate'
    HNOC = 'HNOC Investigate'
    WIRELESS = 'Wireless Repair Intervention Needed'


class ChangeTicketSeverityStatus(Enum):
    CHANGED_TO_LINK_DOWN_SEVERITY = auto()
    CHANGED_TO_EDGE_DOWN_SEVERITY = auto()
    NOT_CHANGED = auto()
