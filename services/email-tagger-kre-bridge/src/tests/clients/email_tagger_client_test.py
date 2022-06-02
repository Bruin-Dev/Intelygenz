import json
from unittest.mock import Mock, call, patch

import grpc
import pytest
from application.clients.email_tagger_client import EmailTaggerClient
from application.clients.generated_grpc import public_input_pb2 as pb2
from application.clients.generated_grpc import public_input_pb2_grpc as pb2_grpc
from asynctest import CoroutineMock
from config import testconfig
from google.protobuf.json_format import Parse


class TestEmailTaggerClient:
    valid_email_data = {"email": {"email_id": "123", "body": "test body", "subject": "test subject"}}
    valid_metrics_data = {
        "original_email": {
            "email": {
                "email_id": "2726244",
                "date": "2016-08-29T09:12:33:001Z",
                "subject": "email_subject",
                "body": "email_body",
                "parent_id": "2726243",
            },
            "tag_ids": ["1003", "1002", "1001"],
        },
        "ticket": {
            "ticket_id": 123456,
            "call_type": "chg",
            "category": "aac",
            "creation_date": "2016-08-29T09:12:33:001Z",
        },
    }
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
        logger = Mock()
        config = Mock()

        kre_client = EmailTaggerClient(logger, config)

        assert kre_client._logger is logger
        assert kre_client._config is config

    @pytest.mark.asyncio
    async def get_prediction_200_test(self):
        mock_prediction_response = {
            "prediction": [
                {"tag_id": "1004", "probability": 0.67},
                {"tag_id": "1001", "probability": 0.27},
                {"tag_id": "1002", "probability": 0.03},
            ]
        }

        mock_stub_prediction_response = self.__data_to_grpc_message(mock_prediction_response, pb2.PredictionResponse())

        logger = Mock()
        stub = Mock()

        stub.GetPrediction = CoroutineMock(return_value=mock_stub_prediction_response)

        exp_prediction_response = {
            "body": mock_prediction_response,
            "status": 200,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            prediction_response = await kre_client.get_prediction(self.valid_email_data)

        assert prediction_response == exp_prediction_response
        stub.GetPrediction.assert_awaited_once_with(
            self.__data_to_grpc_message(self.valid_email_data, pb2.PredictionRequest()), timeout=120
        )

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def get_prediction_grpc_exception_test(self, grpc_code, grpc_detail, expected_status):
        logger = Mock()

        stub = Mock()
        stub.GetPrediction = CoroutineMock()
        stub.GetPrediction.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_prediction_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            prediction_response = await kre_client.get_prediction(self.valid_email_data)

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert prediction_response == exp_prediction_response
        stub.GetPrediction.assert_awaited_once_with(
            self.__data_to_grpc_message(self.valid_email_data, pb2.PredictionRequest()), timeout=120
        )

    @pytest.mark.asyncio
    async def get_prediction_exception_test(self):
        raised_error = "Error current exception test"
        logger = Mock()

        stub = Mock()
        stub.GetPrediction = CoroutineMock()
        stub.GetPrediction.side_effect = Exception(raised_error)

        exp_prediction_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            prediction_response = await kre_client.get_prediction(self.valid_email_data)

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert prediction_response == exp_prediction_response
        stub.GetPrediction.assert_awaited_once_with(
            self.__data_to_grpc_message(self.valid_email_data, pb2.PredictionRequest()), timeout=120
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_200_test(self):
        mock_metric_response = "Saved 1 metrics"

        mock_stub_metric_response = self.__data_to_grpc_message(
            {"message": mock_metric_response}, pb2.SaveMetricsResponse()
        )

        logger = Mock()

        stub = Mock()
        stub.SaveMetrics = CoroutineMock(return_value=mock_stub_metric_response)

        exp_save_metric_response = {
            "body": mock_metric_response,
            "status": 200,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            save_metrics_response = await kre_client.save_metrics(
                email_data=self.valid_metrics_data["original_email"], ticket_data=self.valid_metrics_data["ticket"]
            )

            assert logger.info.call_count == 1
            assert save_metrics_response == exp_save_metric_response
            stub.SaveMetrics.assert_awaited_once_with(
                self.__data_to_grpc_message(self.valid_metrics_data, pb2.SaveMetricsRequest()), timeout=120
            )

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    @pytest.mark.asyncio
    async def post_automation_metrics_exception_errors_test(self, grpc_code, grpc_detail, expected_status):
        logger = Mock()

        stub = Mock()
        stub.SaveMetrics = CoroutineMock()
        stub.SaveMetrics.side_effect = self.__mock_grpc_exception(grpc_code, grpc_detail)

        exp_save_metric_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            save_metrics_response = await kre_client.save_metrics(
                email_data=self.valid_metrics_data["original_email"], ticket_data=self.valid_metrics_data["ticket"]
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert save_metrics_response == exp_save_metric_response
        stub.SaveMetrics.assert_awaited_once_with(
            self.__data_to_grpc_message(self.valid_metrics_data, pb2.SaveMetricsRequest()), timeout=120
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_exception_test(self):
        raised_error = "Error current exception test"
        logger = Mock()

        stub = Mock()
        stub.SaveMetrics = CoroutineMock()
        stub.SaveMetrics.side_effect = Exception(raised_error)

        exp_save_metric_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        kre_client = EmailTaggerClient(logger, testconfig)

        with patch.object(pb2_grpc, "EntrypointStub", return_value=stub):
            save_metrics_response = await kre_client.save_metrics(
                email_data=self.valid_metrics_data["original_email"], ticket_data=self.valid_metrics_data["ticket"]
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert save_metrics_response == exp_save_metric_response
        stub.SaveMetrics.assert_awaited_once_with(
            self.__data_to_grpc_message(self.valid_metrics_data, pb2.SaveMetricsRequest()), timeout=120
        )
