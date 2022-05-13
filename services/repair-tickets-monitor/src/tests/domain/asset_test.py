from unittest.mock import ANY

from application.domain.asset import Assets, Asset, Topic


class TestAsset:
    def allowed_assets_are_properly_queried_test(self):
        topic_a = Topic(call_type=ANY, category="A")
        topic_b = Topic(call_type=ANY, category="B")
        topic_c = Topic(call_type=ANY, category="C")
        asset_1 = Asset(id=ANY, topics=[topic_a])
        asset_2 = Asset(id=ANY, topics=[topic_a, topic_b])
        asset_3 = Asset(id=ANY, topics=[topic_b])
        asset_4 = Asset(id=ANY, topics=[topic_b, topic_c])

        assets = Assets()
        assets.append(Asset(id=ANY, topics=[topic_a]))
        assets.append(Asset(id=ANY, topics=[topic_a, topic_b]))
        assets.append(Asset(id=ANY, topics=[topic_b]))
        assets.append(Asset(id=ANY, topics=[topic_b, topic_c]))

        assert assets.get_allowed_for("A") == [asset_1, asset_2]
        assert assets.get_allowed_for("B") == [asset_2, asset_3, asset_4]
        assert assets.get_allowed_for("C") == [asset_4]
