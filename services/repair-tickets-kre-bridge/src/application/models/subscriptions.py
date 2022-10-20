from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class SaveOutputs(Subscription):
    subject: str = "rta.save_outputs.request"
    queue: str = "rta_kre_bridge"


@dataclass(kw_only=True)
class GetInference(Subscription):
    subject: str = "rta.prediction.request"
    queue: str = "rta_kre_bridge"


@dataclass(kw_only=True)
class SaveCreatedTicketFeedback(Subscription):
    subject: str = "rta.created_ticket_feedback.request"
    queue: str = "rta_kre_bridge"


@dataclass(kw_only=True)
class SaveClosedTicketFeedback(Subscription):
    subject: str = "rta.closed_ticket_feedback.request"
    queue: str = "rta_kre_bridge"
