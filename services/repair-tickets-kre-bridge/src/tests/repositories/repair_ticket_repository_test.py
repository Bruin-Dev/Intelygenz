from unittest.mock import AsyncMock, Mock

import pytest
from application.repositories.repair_ticket_repository import RepairTicketRepository


class TestRepairTicketRepository:
    def instance_test(self):
        client = Mock()

        repository = RepairTicketRepository(client)

        assert repository._kre_client is client

    @pytest.mark.asyncio
    async def get_email_inference__ok_test(self, valid_inference_request, valid_inference_response):
        kre_client = Mock()
        kre_client.get_email_inference = AsyncMock(return_value=valid_inference_response)

        kre_repository = RepairTicketRepository(kre_client)
        inference = await kre_repository.get_email_inference(email_data=valid_inference_request)

        kre_repository._kre_client.get_email_inference.assert_awaited_once_with(valid_inference_request)
        assert inference == valid_inference_response

    @pytest.mark.asyncio
    async def get_email_inference__not_200_from_client_test(self, valid_inference_request):
        expected_response = {"body": "Error from get_email_inference client", "status": 500}

        kre_client = Mock()
        kre_client.get_email_inference = AsyncMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(kre_client)

        response = await kre_repository.get_email_inference(valid_inference_request)

        kre_repository._kre_client.get_email_inference.assert_awaited_once_with(valid_inference_request)
        assert response == expected_response

    @pytest.mark.asyncio
    async def save_outputs__ok_test(self, valid_output_request, valid_output_response):
        kre_client = Mock()
        kre_client.save_outputs = AsyncMock(return_value=valid_output_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_outputs(valid_output_request)
        kre_repository._kre_client.save_outputs.assert_awaited_once_with(valid_output_request)
        assert save_outputs_response == valid_output_response

    @pytest.mark.asyncio
    async def save_outputs__not_2xx_test(self, valid_output_request):
        expected_response = {"body": "Error response", "status": 500}
        kre_client = Mock()
        kre_client.save_outputs = AsyncMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_outputs(valid_output_request)
        kre_repository._kre_client.save_outputs.assert_awaited_once_with(valid_output_request)
        assert save_outputs_response == expected_response

    @pytest.mark.asyncio
    async def save_created_ticket__ok_test(self, valid_created_ticket_request, valid_created_ticket_response):
        kre_client = Mock()
        kre_client.save_created_ticket_feedback = AsyncMock(return_value=valid_created_ticket_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_created_ticket_feedback(valid_created_ticket_request)
        kre_repository._kre_client.save_created_ticket_feedback.assert_awaited_once_with(valid_created_ticket_request)
        assert save_outputs_response == valid_created_ticket_response

    @pytest.mark.asyncio
    async def save_created_ticket__not_2xx_test(self, valid_created_ticket_request):
        expected_response = {"body": "Error response", "status": 500}

        kre_client = Mock()
        kre_client.save_created_ticket_feedback = AsyncMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_created_ticket_feedback(valid_created_ticket_request)
        kre_repository._kre_client.save_created_ticket_feedback.assert_awaited_once_with(valid_created_ticket_request)
        assert save_outputs_response == expected_response

    @pytest.mark.asyncio
    async def save_closed_ticket__ok_test(self, valid_closed_ticket_request__cancelled, valid_closed_ticket_response):
        kre_client = Mock()
        kre_client.save_closed_ticket_feedback = AsyncMock(return_value=valid_closed_ticket_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_closed_ticket_feedback(valid_closed_ticket_request__cancelled)
        kre_repository._kre_client.save_closed_ticket_feedback.assert_awaited_once_with(
            valid_closed_ticket_request__cancelled
        )
        assert save_outputs_response == valid_closed_ticket_response

    @pytest.mark.asyncio
    async def save_closed_ticket__not_2xx_test(self, valid_closed_ticket_request__resolved):
        expected_response = {"body": "Error response", "status": 500}

        kre_client = Mock()
        kre_client.save_closed_ticket_feedback = AsyncMock(return_value=expected_response)

        kre_repository = RepairTicketRepository(kre_client)

        save_outputs_response = await kre_repository.save_closed_ticket_feedback(valid_closed_ticket_request__resolved)
        kre_repository._kre_client.save_closed_ticket_feedback.assert_awaited_once_with(
            valid_closed_ticket_request__resolved
        )
        assert save_outputs_response == expected_response
