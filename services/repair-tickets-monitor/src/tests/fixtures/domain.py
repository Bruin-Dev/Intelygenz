from typing import Callable, List

from application.domain.asset import AssetId
from application.domain.email import Email, EmailTag
from dataclasses import dataclass, field
from pytest import fixture


@fixture(scope="function")
def make_asset_id() -> Callable[..., AssetId]:
    def builder(
        client_id: str = "any_client_id", site_id: str = "any_site_id", service_number: str = "any_service_number"
    ) -> AssetId:
        return AssetId(client_id=client_id, site_id=site_id, service_number=service_number)

    return builder


@dataclass
class AnyEmailTag(EmailTag):
    type: str = "any_type"
    probability: float = 1.0


@dataclass
class AnyEmail(Email):
    id: str = "any_id"
    client_id: str = "any_client_id"
    date: str = "any_date"
    subject: str = "any_subject"
    body: str = "any_body"
    tag: EmailTag = AnyEmailTag()
    sender_address: str = "any_sender_address"
    recipient_addresses: List[str] = field(default_factory=lambda: ["any_recipient_address"])
    cc_addresses: List[str] = field(default_factory=lambda: ["any_cc_address"])
