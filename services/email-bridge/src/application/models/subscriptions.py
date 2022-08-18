from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetEmails(Subscription):
    subject: str = "get.email.request"
    queue: str = "email_bridge"


@dataclass(kw_only=True)
class MarkEmailAsRead(Subscription):
    subject: str = "mark.email.read.request"
    queue: str = "email_bridge"


@dataclass(kw_only=True)
class SendToEmail(Subscription):
    subject: str = "notification.email.request"
    queue: str = "email_bridge"
