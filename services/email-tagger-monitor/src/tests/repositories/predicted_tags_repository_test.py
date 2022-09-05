from unittest.mock import Mock

from application.repositories.predicted_tags_repository import PredictedTagsRepository
from config import testconfig


class TestPredictedTagsRepository:
    def instance_test(self):
        config = testconfig
        notifications_repository = Mock()
        storage_repository = Mock()

        predicted_tags_repository = PredictedTagsRepository(config, notifications_repository, storage_repository)

        assert predicted_tags_repository._config is config
        assert predicted_tags_repository._notifications_repository is notifications_repository
        assert predicted_tags_repository._storage_repository is storage_repository

    def get_pending_tags_ok_test(self, notifications_repository, storage_repository):
        storage_repository.find_all = Mock(return_value=[])
        predicted_tags_repository = PredictedTagsRepository(testconfig, notifications_repository, storage_repository)

        actual = predicted_tags_repository.get_pending_tags()

        storage_repository.find_all.assert_called_once()
        assert actual == []

    def save_new_tag_ok_test(self, notifications_repository, storage_repository):
        storage_repository.save = Mock()
        storage_repository.expire = Mock()
        predicted_tags_repository = PredictedTagsRepository(testconfig, notifications_repository, storage_repository)

        expected_tag = "tag_email_123456"
        tag_data = {"email_id": "123456", "tag_id": "123", "tag_probability": 0.9}
        response = predicted_tags_repository.save_new_tag(**tag_data)

        storage_repository.save.assert_called_once_with(expected_tag, tag_data)
        storage_repository.expire.assert_called_once_with(expected_tag, seconds=300)
        assert response is None
