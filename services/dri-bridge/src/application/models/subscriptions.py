from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetDriParameters(Subscription):
    subject: str = "dri.parameters.request"
    queue: str = "dri_bridge"
