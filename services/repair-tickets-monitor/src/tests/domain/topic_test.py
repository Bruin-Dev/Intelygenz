from unittest.mock import Mock

from application.domain.topic import Topic


class TestTopic:
    def instance_test(self):
        call_type, category = Mock(str), Mock(str)

        subject = Topic(call_type, category)

        assert subject.call_type == call_type
        assert subject.category == category
