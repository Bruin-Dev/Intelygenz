from unittest.mock import Mock
from asynctest import CoroutineMock

import pytest

from application.repositories.repair_ticket_repository import RepairTicketRepository


class TestRepairTicketRepository:

    def instance_test(self):
        logger = Mock()
        client = Mock()

        repository = RepairTicketRepository(logger, client)

        assert repository._logger is logger
        assert repository._kre_client is client

    @pytest.mark.asyncio
    async def get_email_inference_200_test(self, valid_inference_request, valid_inference_response):
        logger = Mock()

        kre_client = Mock()
        kre_client.get_email_inference = CoroutineMock(return_value=valid_inference_response)

        kre_repository = RepairTicketRepository(logger, kre_client)
        prediction = await kre_repository.get_email_inference(email_data=valid_inference_request)

        kre_repository._kre_client.get_email_inference.assert_awaited_once_with(valid_inference_request)
        assert prediction == valid_inference_response

    @pytest.mark.asyncio
    async def get_email_inference_not_200_from_client_test(self, valid_inference_request):
        expected_response = {
            "body": "Error from get_email_inference client",
            "status": 500
        }

        logger = Mock()
        kre_client = Mock()
        kre_client.get_email_inference = CoroutineMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(logger, kre_client)

        response = await kre_repository.get_email_inference(valid_inference_request)

        kre_repository._kre_client.get_email_inference.assert_awaited_once_with(valid_inference_request)
        assert response == expected_response

    @pytest.mark.asyncio
    async def save_outputs_test(self, sa):
        return_value = {"body": "Saved 1 metrics", "status": 200}

        logger = Mock()
        kre_client = Mock()
        kre_client.save_outputs = CoroutineMock(return_value=return_value)

        kre_repository = RepairTicketRepository(logger, kre_client)

        save_outputs_response = await kre_repository.save_outputs(
            email_data=self.valid_metrics_data["original_email"],
            ticket_data=self.valid_metrics_data["ticket"]
        )
        kre_repository._kre_client.save_outputs.assert_awaited_once_with(
            self.valid_metrics_data["original_email"],
            self.valid_metrics_data["ticket"],
        )
        assert save_outputs_response == return_value
