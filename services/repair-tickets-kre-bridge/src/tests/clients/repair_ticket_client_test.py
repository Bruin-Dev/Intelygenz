import json
from unittest import mock
from unittest.mock import AsyncMock, Mock, patch

import grpc
import pytest
from application.clients.generated_grpc import public_input_pb2 as pb2
from application.clients.generated_grpc import public_input_pb2_grpc as pb2_grpc
from application.clients.repair_ticket_client import RepairTicketClient
from config import testconfig
from google.protobuf.json_format import Parse


class TestRepairTicketClient:
    grpc_errors_cases = [
        (grpc.StatusCode.INTERNAL, "Detail test INTERNAL error", 400),
        (grpc.StatusCode.UNAUTHENTICATED, "Detail test UNAUTHENTICATED error", 401),
        (grpc.StatusCode.PERMISSION_DENIED, "Detail test PERMISSION_DENIED error", 403),
        (grpc.StatusCode.UNIMPLEMENTED, "Detail test UNIMPLEMENTED error", 404),
        (grpc.StatusCode.DEADLINE_EXCEEDED, "Detail test DEADLINE_EXCEEDED error", 408),
        (grpc.StatusCode.DATA_LOSS, "Detail test OTHERS error", 500),
    ]

    grpc_errors_cases_ids = [
        "400",
        "401",
        "403",
        "404",
        "408",
        "500",
    ]

    @staticmethod
    def __data_to_grpc_message(data, pb2_msg_descriptor):
        return Parse(json.dumps(data).encode("utf8"), pb2_msg_descriptor, ignore_unknown_fields=False)

    @staticmethod
    def __mock_grpc_exception(grpc_code, grpc_detail):
        grpc_e = grpc.RpcError()
        grpc_e.details = lambda: grpc_detail
        grpc_e.code = lambda: grpc_code
        return grpc_e

    def instance_test(self):
        config = Mock()

        kre_client = RepairTicketClient(config)

        assert kre_client._config is config

    @pytest.mark.asyncio
    async def get_email_inference_200_test(
        self,
        valid_inference_request,
        valid_inference_response,
    ):
        inference_response_data = valid_inference_response["body"]
        mock_stub_prediction_response = self.__data_to_grpc_message(inference_response_data, pb2.PredictionResponse())

        stub = Mock()

        stub.GetPrediction = AsyncMock(return_value=mock_stub_prediction_response)

        kre_client = RepairTicketClient(testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            inference_response = await kre_client.get_email_inference(valid_inference_request)

        assert inference_response == valid_inference_response
        stub.GetPrediction.assert_awaited_once_with(
            self.__data_to_grpc_message({"email": valid_inference_request}, pb2.PredictionRequest()), timeout=120
        )

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def get_email_inference_grpc_exception_test(
        self, grpc_code, grpc_detail, expected_status, valid_inference_request
    ):

        stub = Mock()
        stub.GetPrediction = AsyncMock()
        stub.GetPrediction.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_prediction_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                prediction_response = await kre_client.get_email_inference(valid_inference_request)

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert prediction_response == exp_prediction_response

    @pytest.mark.asyncio
    async def get_email_inference_exception_test(self, valid_inference_request):
        raised_error = "Error current exception test"

        stub = Mock()
        stub.GetPrediction = AsyncMock()
        stub.GetPrediction.side_effect = Exception(raised_error)

        exp_prediction_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                prediction_response = await kre_client.get_email_inference(valid_inference_request)

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert prediction_response == exp_prediction_response

    @pytest.mark.asyncio
    async def save_outputs_200_test(self, valid_output_response, valid_output_request):
        mock_stub_save_outputs_response = self.__data_to_grpc_message(
            valid_output_response["body"], pb2.SaveOutputsResponse()
        )

        stub = Mock()
        stub.SaveOutputs = AsyncMock(return_value=mock_stub_save_outputs_response)

        kre_client = RepairTicketClient(testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            save_outputs_response = await kre_client.save_outputs(valid_output_request)

            assert save_outputs_response == valid_output_response
            stub.SaveOutputs.assert_awaited_once_with(
                self.__data_to_grpc_message(valid_output_request, pb2.SaveOutputsRequest()), timeout=120
            )

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def save_outputs_grpc_exception_errors_test(
        self, grpc_code, grpc_detail, expected_status, valid_output_request
    ):

        stub = Mock()
        stub.SaveOutputs = AsyncMock()
        stub.SaveOutputs.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_save_outputs_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_outputs_response = await kre_client.save_outputs(valid_output_request)

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_outputs_response == exp_save_outputs_response

    @pytest.mark.asyncio
    async def save_outputs_exception_test(self, valid_output_request):
        raised_error = "Error current exception test"

        stub = Mock()
        stub.SaveOutputs = AsyncMock()
        stub.SaveOutputs.side_effect = Exception(raised_error)

        exp_save_output_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_outputs_response = await kre_client.save_outputs(
                    valid_output_request,
                )

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_outputs_response == exp_save_output_response

    @pytest.mark.asyncio
    async def save_created_ticket_feedback_200_test(
        self,
        valid_created_ticket_request,
        valid_created_ticket_response,
    ):
        mock_stub_save_create_tickets_feedback_response = self.__data_to_grpc_message(
            valid_created_ticket_response["body"], pb2.SaveCreatedTicketsFeedbackResponse()
        )

        stub = Mock()
        stub.SaveCreatedTicketsFeedback = AsyncMock(return_value=mock_stub_save_create_tickets_feedback_response)

        kre_client = RepairTicketClient(testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            saved_created_ticket_response = await kre_client.save_created_ticket_feedback(valid_created_ticket_request)

            assert saved_created_ticket_response == valid_created_ticket_response
            stub.SaveCreatedTicketsFeedback.assert_awaited_once_with(
                self.__data_to_grpc_message(valid_created_ticket_request, pb2.SaveCreatedTicketsFeedbackRequest()),
                timeout=120,
            )

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def save_created_ticket_grpc_feedback_exception_test(
        self, grpc_code, grpc_detail, expected_status, valid_created_ticket_request
    ):

        stub = Mock()
        stub.SaveCreatedTicketsFeedback = AsyncMock()
        stub.SaveCreatedTicketsFeedback.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_save_created_ticket_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_created_ticket_response = await kre_client.save_created_ticket_feedback(
                    valid_created_ticket_request
                )

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_created_ticket_response == exp_save_created_ticket_response

    @pytest.mark.asyncio
    async def save_created_ticket_feedback_non_2xx_test(self, valid_created_ticket_request):
        raised_error = "Error current exception test"

        stub = Mock()
        stub.SaveCreatedTicketsFeedback = AsyncMock()
        stub.SaveCreatedTicketsFeedback.side_effect = Exception(raised_error)

        exp_save_created_ticket_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_created_ticket_response = await kre_client.save_created_ticket_feedback(
                    valid_created_ticket_request,
                )

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_created_ticket_response == exp_save_created_ticket_response

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_200_cancelled_test(
        self,
        valid_closed_ticket_request__cancelled,
        valid_closed_ticket_response,
    ):
        mock_stub_save_closed_tickets_feedback_response = self.__data_to_grpc_message(
            valid_closed_ticket_response["body"], pb2.SaveClosedTicketsFeedbackResponse()
        )

        stub = Mock()
        stub.SaveClosedTicketsFeedback = AsyncMock(return_value=mock_stub_save_closed_tickets_feedback_response)

        kre_client = RepairTicketClient(testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            saved_closed_ticket_response = await kre_client.save_closed_ticket_feedback(
                valid_closed_ticket_request__cancelled
            )

        assert saved_closed_ticket_response == valid_closed_ticket_response
        stub.SaveClosedTicketsFeedback.assert_awaited_once_with(
            self.__data_to_grpc_message(valid_closed_ticket_request__cancelled, pb2.SaveClosedTicketsFeedbackRequest()),
            timeout=120,
        )

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_200_resolved_test(
        self,
        valid_closed_ticket_request__resolved,
        valid_closed_ticket_response,
    ):
        mock_stub_save_closed_tickets_feedback_response = self.__data_to_grpc_message(
            valid_closed_ticket_response["body"], pb2.SaveClosedTicketsFeedbackResponse()
        )

        stub = Mock()
        stub.SaveClosedTicketsFeedback = AsyncMock(return_value=mock_stub_save_closed_tickets_feedback_response)

        kre_client = RepairTicketClient(testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            saved_closed_ticket_response = await kre_client.save_closed_ticket_feedback(
                valid_closed_ticket_request__resolved
            )

        assert saved_closed_ticket_response == valid_closed_ticket_response
        stub.SaveClosedTicketsFeedback.assert_awaited_once_with(
            self.__data_to_grpc_message(valid_closed_ticket_request__resolved, pb2.SaveClosedTicketsFeedbackRequest()),
            timeout=120,
        )

    @pytest.mark.asyncio
    async def save_closed_ticket_feedback_exception_test(self, valid_closed_ticket_request__resolved):
        raised_error = "Error current exception test"

        stub = Mock()
        stub.SaveClosedTicketsFeedback = AsyncMock()
        stub.SaveClosedTicketsFeedback.side_effect = Exception(raised_error)

        exp_save_closed_ticket_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_closed_ticket_response = await kre_client.save_closed_ticket_feedback(
                    valid_closed_ticket_request__resolved,
                )

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_closed_ticket_response == exp_save_closed_ticket_response

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def save_closed_ticket_grpc_feedback_exception_test(
        self, grpc_code, grpc_detail, expected_status, valid_closed_ticket_request__cancelled
    ):

        stub = Mock()
        stub.SaveClosedTicketsFeedback = AsyncMock()
        stub.SaveClosedTicketsFeedback.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_save_closed_ticket_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = RepairTicketClient(testconfig)

        with mock.patch("application.clients.repair_ticket_client.logger") as logger:
            with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
                save_closed_ticket_response = await kre_client.save_closed_ticket_feedback(
                    valid_closed_ticket_request__cancelled
                )

                assert logger.info.call_count == 0
                assert logger.error.call_count == 1
                assert save_closed_ticket_response == exp_save_closed_ticket_response
