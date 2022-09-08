from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class ReportIncident(Subscription):
    subject: str = "servicenow.incident.report.request"
    queue: str = "servicenow_bridge"
