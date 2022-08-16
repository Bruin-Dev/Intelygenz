from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class TemplateExample(Subscription):
    subject: str = "template.example"
    queue: str = "forticloud_bridge"
