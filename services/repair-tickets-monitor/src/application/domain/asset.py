from typing import List

from dataclasses import dataclass


@dataclass
class Assets(List['Asset']):
    def get_by_allowed_topic_category(self, category: str):
        return [asset for asset in self if asset.is_topic_category_allowed(category)]


@dataclass
class Asset:
    """
    Data structure that represents a Bruin asset
    """
    id: 'AssetId'
    allowed_topics: List['Topic']

    def is_topic_category_allowed(self, category: str):
        return any([allowed_topic.category == category for allowed_topic in self.allowed_topics])


@dataclass
class AssetId:
    """
    Data structure that represents a Bruin asset identification.
    """
    service_number: str
    client_id: int
    site_id: int


@dataclass
class Topic:
    """
    Data structure that represents a Bruin topic.
    """
    call_type: str
    category: str
