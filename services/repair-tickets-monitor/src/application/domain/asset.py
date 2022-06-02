from typing import List

from dataclasses import dataclass


class Assets(List["Asset"]):
    def with_allowed_category(self, category: str) -> "Assets":
        return Assets(asset for asset in self if asset.is_allowed_for(category))

    def with_no_topics(self) -> "Assets":
        return Assets(asset for asset in self if not asset.allowed_topics)


@dataclass
class Asset:
    """
    Data structure that represents a Bruin asset
    """

    id: "AssetId"
    allowed_topics: List["Topic"]

    def is_allowed_for(self, category: str) -> bool:
        return any(allowed_topic.category == category for allowed_topic in self.allowed_topics)


@dataclass
class AssetId:
    """
    Data structure that represents a Bruin asset identification.
    """

    client_id: str
    site_id: str
    service_number: str


@dataclass
class Topic:
    """
    Data structure that represents a Bruin topic.
    """

    call_type: str
    category: str
