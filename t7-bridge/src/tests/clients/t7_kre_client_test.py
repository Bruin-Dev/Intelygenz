import json
from google.protobuf.json_format import Parse, ParseDict
from unittest.mock import patch
from unittest.mock import Mock

from config import testconfig

from application.clients import public_input_pb2 as pb2, public_input_pb2_grpc as pb2_grpc
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

    def instance_test(self):
        logger = Mock()
        config = Mock()

        t7_kre_client = T7KREClient(logger, config)

        assert t7_kre_client._logger is logger
        assert t7_kre_client._config is config

    def get_prediction_200_test(self):
        prediction_request = self.__create_request(
            pb2.PredictionRequest(),
            self.valid_ticket_id,
            self.valid_ticket_rows
        )

        exp_prediction_response = {
            "assetPredictions": [
                {
                    "asset": "some_serial_number",
                    "taskResults": [{
                        "name": "Some action",
                        "probability": 0.94843847
                    }]
                }
            ]
        }

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.Prediction = Mock(
            return_value=self.__create_prediction_response_mock(exp_prediction_response)
        )

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock):
            prediction_response = t7_kre_client.get_prediction(
                ticket_id=self.valid_ticket_id,
                ticket_rows=self.valid_ticket_rows
            )

            assert logger.info.called

            response_mock.Prediction.assert_called_once()
            response_mock.Prediction.assert_called_once_with(prediction_request, timeout=120)

            assert prediction_response == {
                "body": exp_prediction_response,
                "status": 200,
            }

    def post_automation_metrics_200_test(self):
        metrics_request = self.__create_request(
            pb2.SaveMetricsRequest(),
            self.valid_ticket_id,
            self.valid_ticket_rows
        )

        exp_metric_response = "Saved 1 metrics"

        logger = Mock()
        logger.info = Mock()

        response_mock = Mock()
        response_mock.SaveMetrics = Mock(
            return_value=self.__create_save_metrics_response_mock(exp_metric_response)
        )

        t7_kre_client = T7KREClient(logger, testconfig)

        with patch.object(pb2_grpc, 'EntrypointStub', return_value=response_mock):
            save_metrics_response = t7_kre_client.post_automation_metrics(self.valid_ticket_id, self.valid_ticket_rows)

            assert logger.info.called

            response_mock.SaveMetrics.assert_called_once()
            response_mock.SaveMetrics.assert_called_once_with(metrics_request, timeout=120)

            assert save_metrics_response == {
                "body": exp_metric_response,
                "status": 200,
            }

    @staticmethod
    def __create_prediction_response_mock(exp_prediction_response):
        prediction_response_mock = pb2.PredictionResponse()

        for asset_prediction in exp_prediction_response["assetPredictions"]:
            prediction = ParseDict({
                "asset": asset_prediction["asset"]
            }, pb2.AssetPrediction())

            for task_result in asset_prediction["taskResults"]:
                prediction.task_results.append(ParseDict(
                    task_result,
                    pb2.TaskResult()
                ))

            prediction_response_mock.asset_predictions.append(prediction)
        return prediction_response_mock

    @staticmethod
    def __create_save_metrics_response_mock(exp_save_metrics_response):
        save_metrics_response_mock = pb2.SaveMetricsResponse()
        save_metrics_response_mock.message = exp_save_metrics_response

        return save_metrics_response_mock

    @staticmethod
    def __create_request(request, ticket_id, ticket_rows):
        request.ticket_id = ticket_id
        for row in ticket_rows:
            ticket_row = Parse(json.dumps(row), pb2.TicketRow())
            request.ticket_rows.append(ticket_row)

        return request
