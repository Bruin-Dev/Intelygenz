from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class SendToSlack(Subscription):
    subject: str = "notification.slack.request"
    queue: str = "notifications_bridge"
