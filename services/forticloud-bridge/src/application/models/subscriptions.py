from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetApData(Subscription):
    subject: str = "request.ap.data"
    queue: str = "forticloud_bridge"


@dataclass(kw_only=True)
class GetSwitchesData(Subscription):
    subject: str = "request.switches.data"
    queue: str = "forticloud_bridge"
