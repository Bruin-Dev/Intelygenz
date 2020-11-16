import json
import grpc
from google.protobuf.json_format import Parse, MessageToDict

from application.clients import public_input_pb2 as pb2
from application.clients import public_input_pb2_grpc as pb2_grpc


class T7KREClient:

    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

    def _create_stub(self):
        credentials = grpc.ssl_channel_credentials()
        c = grpc.secure_channel(f"{self._config.KRE_CONFIG['base_url']}", credentials=credentials)
        return pb2_grpc.EntrypointStub(c)

    @staticmethod
    def __create_request(request, ticket_id, ticket_rows):
        request.ticket_id = ticket_id
        for row in ticket_rows:
            ticket_row = Parse(json.dumps(row), pb2.TicketRow())
            request.ticket_rows.append(ticket_row)

        return request

    def get_prediction(self, ticket_id, ticket_rows):
        try:
            stub = self._create_stub()

            request = self.__create_request(
                pb2.PredictionRequest(),
                ticket_id,
                ticket_rows
            )

            save_prediction_response = stub.Prediction(request, timeout=120)
            dic_prediction_response = MessageToDict(save_prediction_response)
            response = {
                "body": dic_prediction_response,
                "status": 200,
            }
            self._logger.info(f'Got response getting predictions from KRE: {dic_prediction_response}')

        except grpc.RpcError as kre_e:
            response = {
                "body": f"Error details for {kre_e.code()}: {kre_e.details}",
                "status": 500
            }
            self._logger.error(f'Got error getting predictions from KRE: {kre_e.code()}: {kre_e.details}')

        except Exception as kre_e:
            response = {
                "body": f"Error: {kre_e.args[0]}",
                "status": 500
            }
            self._logger.error(f'Got error getting predictions from KRE: {kre_e.args[0]}')

        return response

    def post_automation_metrics(self, ticket_id, ticket_rows):
        try:
            stub = self._create_stub()

            request = self.__create_request(
                pb2.SaveMetricsRequest(),
                ticket_id,
                ticket_rows
            )

            save_metrics_response = stub.SaveMetrics(request, timeout=120)
            response = {
                "body": save_metrics_response.message,
                "status": 200
            }

            self._logger.info(f'Got response saving metrics from KRE: {response["body"]}')

        except grpc.RpcError as kre_e:
            response = {
                "body": f"Error details for {kre_e.code()}: {kre_e.details}",
                "status": 500
            }
            self._logger.error(f'Got error saving metrics from KRE: {response["body"]}')

        except Exception as kre_e:
            response = {
                "body": f"Error: {kre_e.args[0]}",
                "status": 500
            }
            self._logger.error(f'Got error saving metrics from KRE: {response["body"]}')

        return response

    def save_prediction(self, prediction_feedback):
        try:
            stub = self._create_stub()

            save_predictions_response = stub.SavePrediction(Parse(
                json.dumps(prediction_feedback).encode('utf8'),
                pb2.SavePredictionRequest()
            ), timeout=120)

            response = {
                "body": save_predictions_response.message,
                "status": 200
            }

            self._logger.info(f'Got response saving predictions from KRE: {response["body"]}')

        except grpc.RpcError as kre_e:
            response = {
                "body": f"Error details for {kre_e.code()}: {kre_e.details}",
                "status": 500
            }
            self._logger.error(f'Got error saving predictions from KRE: {response["body"]}')

        except Exception as kre_e:
            response = {
                "body": f"Error: {kre_e.args[0]}",
                "status": 500
            }
            self._logger.error(f'Got error saving predictions from KRE: {response["body"]}')

        return response
