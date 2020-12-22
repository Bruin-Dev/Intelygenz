import pytest
import json
import grpc
from google.protobuf.json_format import Parse
from unittest.mock import Mock, call, patch

from config import testconfig

from application.clients.generated_grpc import public_input_pb2_grpc as pb2_grpc, public_input_pb2 as pb2
from application.clients.t7_kre_client import T7KREClient


class TestT7KREClient:
    valid_ticket_id = 123
    valid_ticket_rows = [
        {
            "asset": "asset1",
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 1",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 1",
            "sla": 1,
        },
        {
            "asset": None,
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 2",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 2",
            "sla": 1,
        }
    ]

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
        return Parse(
            json.dumps(data).encode('utf8'),
            pb2_msg_descriptor,
            ignore_unknown_fields=False
        )

    @staticmethod
    def __mock_grpc_exception(grpc_code, grpc_detail):
        grpc_e = grpc.RpcError()
        grpc_e.details = lambda: grpc_detail
        grpc_e.code = lambda: grpc_code
        return grpc_e

    def instance_test(self):
        logger = Mock()
        config = Mock()

        t7_kre_client = T7KREClient(logger, config)

        assert t7_kre_client._logger is logger
        assert t7_kre_client._config is config

    def get_prediction_200_test(self):
        mock_prediction_response = {
            "asset_predictions": [
                {
                    "asset": "some_serial_number",
                    "task_results": [{
                        "name": "Some action",
                        "probability": 0.94843847
                    }]
                }
            ]
        }

        mock_stub_prediction_response = self.__data_to_grpc_message(mock_prediction_response, pb2.PredictionResponse())

        logger = Mock()
        logger.info = Mock()

        stub = Mock()
        stub.Prediction = Mock(return_value=mock_stub_prediction_response)

        exp_prediction_response = {
            "body": mock_prediction_response,
            "status": 200,
        }

        exp_stub_prediction_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {
                        "ticket_id": self.valid_ticket_id,
                        "ticket_rows": self.valid_ticket_rows
                    },
                    pb2.PredictionRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            prediction_response = t7_kre_client.get_prediction(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

        assert logger.info.call_count == 1
        assert stub.Prediction.call_args_list == exp_stub_prediction_call_args_list
        assert prediction_response == exp_prediction_response

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    def get_prediction_grpc_exception_test(self, grpc_code, grpc_detail, expected_status):
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        stub = Mock()
        stub.Prediction = Mock()
        stub.Prediction.side_effect = self.__mock_grpc_exception(
            grpc_code,
            grpc_detail
        )

        exp_prediction_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        exp_stub_prediction_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {
                        "ticket_id": self.valid_ticket_id,
                        "ticket_rows": self.valid_ticket_rows
                    },
                    pb2.PredictionRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            prediction_response = t7_kre_client.get_prediction(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert stub.Prediction.call_args_list == exp_stub_prediction_call_args_list
        assert prediction_response == exp_prediction_response

    def get_prediction_exception_test(self):
        raised_error = 'Error current exception test'
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        stub = Mock()
        stub.Prediction = Mock()
        stub.Prediction.side_effect = Exception(raised_error)

        exp_prediction_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        exp_stub_prediction_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {
                        "ticket_id": self.valid_ticket_id,
                        "ticket_rows": self.valid_ticket_rows
                    },
                    pb2.PredictionRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            prediction_response = t7_kre_client.get_prediction(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert stub.Prediction.call_args_list == exp_stub_prediction_call_args_list
        assert prediction_response == exp_prediction_response

    def post_automation_metrics_200_test(self):
        mock_metric_response = "Saved 1 metrics"

        mock_stub_metric_response = self.__data_to_grpc_message(
            {"message": mock_metric_response},
            pb2.SaveMetricsResponse()
        )

        logger = Mock()
        logger.info = Mock()

        stub = Mock()
        stub.SaveMetrics = Mock(return_value=mock_stub_metric_response)

        exp_save_metric_response = {
            "body": mock_metric_response,
            "status": 200,
        }

        exp_stub_save_metrics_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {"ticket_id": self.valid_ticket_id, "ticket_rows": self.valid_ticket_rows},
                    pb2.SaveMetricsRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            save_metrics_response = t7_kre_client.post_automation_metrics(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

            assert logger.info.call_count == 1
            assert stub.SaveMetrics.call_args_list == exp_stub_save_metrics_call_args_list
            assert save_metrics_response == exp_save_metric_response

    @pytest.mark.parametrize("grpc_code, grpc_detail, expected_status", grpc_errors_cases, ids=grpc_errors_cases_ids)
    def post_automation_metrics_exception_errors_test(self, grpc_code, grpc_detail, expected_status):
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        stub = Mock()
        stub.SaveMetrics = Mock()
        stub.SaveMetrics.side_effect = self.__mock_grpc_exception(
            grpc_code,
            grpc_detail
        )

        exp_save_metric_response = {
            "body": f"Grpc error details: {grpc_detail}",
            "status": expected_status,
        }

        exp_stub_save_metrics_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {
                        "ticket_id": self.valid_ticket_id,
                        "ticket_rows": self.valid_ticket_rows
                    },
                    pb2.SaveMetricsRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            save_metrics_response = t7_kre_client.post_automation_metrics(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert stub.SaveMetrics.call_args_list == exp_stub_save_metrics_call_args_list
        assert save_metrics_response == exp_save_metric_response

    def post_automation_metrics_exception_test(self):
        raised_error = 'Error current exception test'
        logger = Mock()
        logger.info = Mock()
        logger.error = Mock()

        stub = Mock()
        stub.SaveMetrics = Mock()
        stub.SaveMetrics.side_effect = Exception(raised_error)

        exp_save_metric_response = {
            "body": f"Error: {raised_error}",
            "status": 500,
        }

        exp_stub_save_metrics_call_args_list = [
            call(
                self.__data_to_grpc_message(
                    {
                        "ticket_id": self.valid_ticket_id,
                        "ticket_rows": self.valid_ticket_rows
                    },
                    pb2.SaveMetricsRequest()
                ),
                timeout=120
            )
        ]

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=stub):
            save_metrics_response = t7_kre_client.post_automation_metrics(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

        assert logger.info.call_count == 0
        assert logger.error.call_count == 1
        assert stub.SaveMetrics.call_args_list == exp_stub_save_metrics_call_args_list
        assert save_metrics_response == exp_save_metric_response
