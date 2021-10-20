from enum import Enum


class Outages(Enum):
    LINK_DOWN = 'Link Down Outage (no HA)'
    HARD_DOWN = 'Hard Down Outage (no HA)'

    HA_LINK_DOWN = 'Link Down Outage (HA)'
    HA_SOFT_DOWN = 'Soft Down Outage (HA)'
    HA_HARD_DOWN = 'Hard Down Outage (HA)'
