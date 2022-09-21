from dataclasses import dataclass

from framework.nats.models import Subscription


@dataclass(kw_only=True)
class DigiReboot(Subscription):
    subject: str = "digi.reboot"
    queue: str = "digi_bridge"


@dataclass(kw_only=True)
class GetDigiRecoveryLogs(Subscription):
    subject: str = "get.digi.recovery.logs"
    queue: str = "digi_bridge"
