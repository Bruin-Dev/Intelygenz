from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetProbes(Subscription):
    subject: str = "hawkeye.probe.request"
    queue: str = "hawkeye_bridge"


@dataclass(kw_only=True)
class GetTestResults(Subscription):
    subject: str = "hawkeye.test.request"
    queue: str = "hawkeye_bridge"
