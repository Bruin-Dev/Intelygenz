from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetPrediction(Subscription):
    subject: str = "email_tagger.prediction.request"
    queue: str = "email_tagger_kre_bridge"


@dataclass(kw_only=True)
class SaveMetrics(Subscription):
    subject: str = "email_tagger.metrics.request"
    queue: str = "email_tagger_kre_bridge"
