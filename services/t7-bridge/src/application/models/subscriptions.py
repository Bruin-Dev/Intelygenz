from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetPrediction(Subscription):
    subject: str = "t7.prediction.request"
    queue: str = "t7_bridge"


@dataclass(kw_only=True)
class PostAutomationMetrics(Subscription):
    subject: str = "t7.automation.metrics"
    queue: str = "t7_bridge"


@dataclass(kw_only=True)
class PostLiveAutomationMetrics(Subscription):
    subject: str = "t7.live.automation.metrics"
    queue: str = "t7_bridge"
