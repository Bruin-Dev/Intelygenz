import json
from typing import List

import grpc
from application.clients.generated_grpc import public_input_pb2 as pb2
from application.clients.generated_grpc import public_input_pb2_grpc as pb2_grpc
from google.protobuf.json_format import MessageToDict, Parse


class T7KREClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

    def _create_stub(self):
        certificates_file = open("/tmp/root-certificates.txt", "a+")
        certificates_file.seek(0)
        root_certificates = bytes(certificates_file.read(), "utf-8")
        credentials = grpc.ssl_channel_credentials(root_certificates=root_certificates)
        c = grpc.secure_channel(f"{self._config.KRE_CONFIG['base_url']}", credentials=credentials)
        return pb2_grpc.EntrypointStub(c)

    @staticmethod
    def __grpc_to_http_status(grpc_code) -> int:
        if grpc.StatusCode.INTERNAL == grpc_code:
            return 400
        elif grpc.StatusCode.UNAUTHENTICATED == grpc_code:
            return 401
        elif grpc.StatusCode.PERMISSION_DENIED == grpc_code:
            return 403
        elif grpc.StatusCode.UNIMPLEMENTED == grpc_code:
            return 404
        elif grpc.StatusCode.DEADLINE_EXCEEDED == grpc_code:
            return 408
        else:
            return 500

    def get_prediction(self, ticket_id: int, ticket_rows: List[dict], assets_to_predict: List[str]) -> dict:
        try:
            stub = self._create_stub()

            save_prediction_response = stub.Prediction(
                Parse(
                    json.dumps(
                        {"ticket_id": ticket_id, "ticket_rows": ticket_rows, "assets_to_predict": assets_to_predict}
                    ).encode("utf8"),
                    pb2.PredictionRequest(),
                    ignore_unknown_fields=True,
                ),
                timeout=120,
            )

            dic_prediction_response = MessageToDict(save_prediction_response, preserving_proto_field_name=True)

            response = {
                "body": dic_prediction_response,
                "status": 200,
            }
            self._logger.info(f"Got response getting predictions from Konstellation: {dic_prediction_response}")

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error getting predictions from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f"Got error getting predictions from Konstellation: {e.args[0]}")

        return response

    def post_automation_metrics(self, ticket_id: int, ticket_rows: List[dict]) -> dict:
        try:
            stub = self._create_stub()

            save_metrics_response = stub.SaveMetrics(
                Parse(
                    json.dumps({"ticket_id": ticket_id, "ticket_rows": ticket_rows}).encode("utf8"),
                    pb2.SaveMetricsRequest(),
                    ignore_unknown_fields=True,
                ),
                timeout=120,
            )

            response = {"body": save_metrics_response.message, "status": 200}

            self._logger.info(f'Got response saving metrics from Konstellation: {response["body"]}')

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error saving metrics from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f'Got error saving metrics from Konstellation: {response["body"]}')

        return response

    def post_live_automation_metrics(self, ticket_id: int, asset_id: str, automated_successfully: bool) -> dict:
        try:
            stub = self._create_stub()

            save_live_metrics_response = stub.SaveLiveMetrics(
                Parse(
                    json.dumps(
                        {"ticket_id": ticket_id, "asset_id": asset_id, "automated_successfully": automated_successfully}
                    ).encode("utf8"),
                    pb2.SaveLiveMetricsRequest(),
                    ignore_unknown_fields=True,
                ),
                timeout=120,
            )

            response = {"body": save_live_metrics_response.message, "status": 200}

            self._logger.info(f'Got response saving live metrics from Konstellation: {response["body"]}')

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error saving live metrics from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f'Got error saving live metrics from Konstellation: {response["body"]}')

        return response
