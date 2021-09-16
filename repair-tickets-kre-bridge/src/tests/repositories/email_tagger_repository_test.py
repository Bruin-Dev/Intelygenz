from unittest.mock import Mock
from asynctest import CoroutineMock

import pytest

from application.repositories.repair_ticket_repository import RepairTicketRepository


class TestRepairTicketRepository:
    valid_email_data = {
        "email_id": 123,
        "client_id": 5678,
        "body": "test body",
        "subject": "test subject"
    }
    valid_metrics_data = {
        "original_email": {
            "email": {
                "email_id": "2726244",
                "date": "2016-08-29T09:12:33:001Z",
                "subject": "email_subject",
                "body": "email_body",
                "parent_id": "2726243",
            },
            "tag_ids": [3, 2, 1]
        },
        "ticket": {
            "ticket_id": 123456,
            "call_type": "chg",
            "category": "aac",
            "creation_date": "2016-08-29T09:12:33:001Z"
        }
    }
    valid_tag_ids = [3, 2, 1]

    def instance_test(self):
        logger = Mock()
        client = Mock()

        repository = RepairTicketRepository(logger, client)

        assert repository._logger is logger
        assert repository._kre_client is client

    @pytest.mark.asyncio
    async def get_prediction_200_test(self):
        prediction_mock = {
            "body": {
                "email_id": 123,
                "prediction": [
                    {"tag_id": "1003", "probability": 0.6},
                    {"tag_id": "1001", "probability": 0.4},
                ]
            },
            "status": 200
        }

        expected_prediction = {
            "body": [
                {"tag_id": "1003", "probability": 0.6},
                {"tag_id": "1001", "probability": 0.4}
            ],
            "status": 200
        }

        logger = Mock()

        kre_client = Mock()
        kre_client.get_prediction = CoroutineMock(return_value=prediction_mock)

        kre_repository = RepairTicketRepository(logger, kre_client)
        prediction = await kre_repository.get_prediction(email_data=self.valid_email_data)

        kre_repository._kre_client.get_prediction.assert_awaited_once_with(self.valid_email_data)
        assert prediction == expected_prediction

    @pytest.mark.asyncio
    async def get_prediction_not_200_from_client_test(self):
        expected_response = {
            "body": "Error from get_prediction client",
            "status": 500
        }

        logger = Mock()
        kre_client = Mock()
        kre_client.get_prediction = CoroutineMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(logger, kre_client)

        response = await kre_repository.get_prediction(self.valid_email_data)

        kre_repository._kre_client.get_prediction.assert_awaited_once_with(self.valid_email_data)
        assert response == expected_response

    @pytest.mark.asyncio
    async def save_metrics_test(self):
        return_value = {"body": "Saved 1 metrics", "status": 200}

        logger = Mock()
        kre_client = Mock()
        kre_client.save_metrics = CoroutineMock(return_value=return_value)

        kre_repository = RepairTicketRepository(logger, kre_client)

        save_metrics_response = await kre_repository.save_metrics(
            email_data=self.valid_metrics_data["original_email"],
            ticket_data=self.valid_metrics_data["ticket"]
        )
        kre_repository._kre_client.save_metrics.assert_awaited_once_with(
            self.valid_metrics_data["original_email"],
            self.valid_metrics_data["ticket"],
        )
        assert save_metrics_response == return_value
