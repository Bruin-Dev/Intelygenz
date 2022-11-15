from unittest.mock import AsyncMock, Mock

import pytest
from application.repositories.email_tagger_repository import EmailTaggerRepository


class TestEmailTaggerRepository:
    valid_email_data = {"email_id": 123, "client_id": 5678, "body": "test body", "subject": "test subject"}
    valid_metrics_data = {
        "original_email": {
            "email": {
                "email_id": "2726244",
                "date": "2016-08-29T09:12:33:001Z",
                "subject": "email_subject",
                "body": "email_body",
                "parent_id": "2726243",
            },
            "tag_ids": [3, 2, 1],
        },
        "ticket": {
            "ticket_id": 123456,
            "call_type": "chg",
            "category": "aac",
            "creation_date": "2016-08-29T09:12:33:001Z",
        },
    }
    valid_tag_ids = [3, 2, 1]

    def instance_test(self):
        client = Mock()

        repository = EmailTaggerRepository(client)

        assert repository._kre_client is client

    @pytest.mark.asyncio
    async def get_prediction_200_test(self):
        prediction_mock = {
            "body": {
                "email_id": 123,
                "prediction": [
                    {"tag_id": "1003", "probability": 0.6},
                    {"tag_id": "1001", "probability": 0.4},
                ],
            },
            "status": 200,
        }

        expected_prediction = {
            "body": [{"tag_id": "1003", "probability": 0.6}, {"tag_id": "1001", "probability": 0.4}],
            "status": 200,
        }

        kre_client = Mock()
        kre_client.get_prediction = AsyncMock(return_value=prediction_mock)

        email_tagger_repository = EmailTaggerRepository(kre_client)
        prediction = await email_tagger_repository.get_prediction(email_data=self.valid_email_data)

        email_tagger_repository._kre_client.get_prediction.assert_awaited_once_with(self.valid_email_data)
        assert prediction == expected_prediction

    @pytest.mark.asyncio
    async def get_prediction_not_200_from_client_test(self):
        expected_response = {"body": "Error from get_prediction client", "status": 500}

        kre_client = Mock()
        kre_client.get_prediction = AsyncMock(return_value=expected_response)

        email_tagger_repository = EmailTaggerRepository(kre_client)

        response = await email_tagger_repository.get_prediction(self.valid_email_data)

        email_tagger_repository._kre_client.get_prediction.assert_awaited_once_with(self.valid_email_data)
        assert response == expected_response

    @pytest.mark.asyncio
    async def save_metrics_test(self):
        return_value = {"body": "Saved 1 metrics", "status": 200}

        kre_client = Mock()
        kre_client.save_metrics = AsyncMock(return_value=return_value)

        email_tagger_repository = EmailTaggerRepository(kre_client)

        save_metrics_response = await email_tagger_repository.save_metrics(
            email_data=self.valid_metrics_data["original_email"], ticket_data=self.valid_metrics_data["ticket"]
        )
        email_tagger_repository._kre_client.save_metrics.assert_awaited_once_with(
            self.valid_metrics_data["original_email"],
            self.valid_metrics_data["ticket"],
        )
        assert save_metrics_response == return_value
