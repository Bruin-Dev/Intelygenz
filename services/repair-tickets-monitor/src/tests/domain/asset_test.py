from unittest.mock import ANY

from application.domain.asset import Assets, Asset, Topic


class TestAsset:
    def allowed_assets_are_properly_queried_test(self):
        topic_a = Topic(call_type="any", category="A")
        topic_b = Topic(call_type="any", category="B")
        topic_c = Topic(call_type="any", category="C")
        asset_1 = Asset(id=ANY, allowed_topics=[topic_a])
        asset_2 = Asset(id=ANY, allowed_topics=[topic_a, topic_b])
        asset_3 = Asset(id=ANY, allowed_topics=[topic_b])
        asset_4 = Asset(id=ANY, allowed_topics=[topic_b, topic_c])

        assets = Assets([asset_1, asset_2, asset_3, asset_4])

        assert assets.with_allowed_category("A") == Assets([asset_1, asset_2])
        assert assets.with_allowed_category("B") == Assets([asset_2, asset_3, asset_4])
        assert assets.with_allowed_category("C") == Assets([asset_4])

    def empty_topics_assets_are_properly_detected_test(self):
        asset_1 = Asset(id=ANY, allowed_topics=[])
        asset_2 = Asset(id=ANY, allowed_topics=[Topic(call_type="any", category="any")])

        assets = Assets([asset_1, asset_2])

        assert assets.with_no_topics() == Assets([asset_1])
