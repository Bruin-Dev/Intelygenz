import json

import grpc
from application.clients.generated_grpc import public_input_pb2 as pb2
from application.clients.generated_grpc import public_input_pb2_grpc as pb2_grpc
from google.protobuf.json_format import MessageToDict, Parse
from grpc import aio as grpc_aio


class RepairTicketClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

    async def _create_stub(self):
        if self._config.KRE_CONFIG["grpc_secure_mode"]:
            credentials = grpc.ssl_channel_credentials()
            c = grpc_aio.secure_channel(f"{self._config.KRE_CONFIG['base_url']}", credentials=credentials)
        else:
            # NOTE: To be used with KRE local env
            c = grpc_aio.insecure_channel(f"{self._config.KRE_CONFIG['base_url']}")

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

    async def get_email_inference(self, email_data: dict) -> dict:
        try:
            stub = await self._create_stub()
            self._logger.info(f"email_data={email_data}")
            email_message = Parse(
                json.dumps({"email": email_data}).encode("utf8"),
                pb2.PredictionRequest(),
                ignore_unknown_fields=False,
            )
            self._logger.info(f"email_message={email_message}.")

            get_prediction_response = await stub.GetPrediction(
                email_message,
                timeout=120,
            )

            dic_prediction_response = MessageToDict(
                get_prediction_response, preserving_proto_field_name=True, including_default_value_fields=True
            )

            response = {
                "body": dic_prediction_response,
                "status": 200,
            }
            self._logger.info(f"Got response getting prediction from Konstellation: {dic_prediction_response}")

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error getting prediction from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f"Got error getting prediction from Konstellation: {e.args[0]}")

        return response

    async def save_outputs(self, payload: dict) -> dict:
        try:
            stub = await self._create_stub()

            save_outputs_response = await stub.SaveOutputs(
                Parse(
                    json.dumps(payload).encode("utf8"),
                    pb2.SaveOutputsRequest(),
                    ignore_unknown_fields=False,
                ),
                timeout=120,
            )

            response = {"body": {"success": save_outputs_response.success}, "status": 200}

            self._logger.info(f'Got response saving outputs from Konstellation: {response["body"]}')

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error saving outputs from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f'Got error saving outputs from Konstellation: {response["body"]}')

        return response

    async def save_created_ticket_feedback(self, payload: dict) -> dict:
        try:
            stub = await self._create_stub()

            save_created_ticket_response = await stub.SaveCreatedTicketsFeedback(
                Parse(
                    json.dumps(payload).encode("utf8"),
                    pb2.SaveCreatedTicketsFeedbackRequest(),
                    ignore_unknown_fields=False,
                ),
                timeout=120,
            )

            response = {"body": {"success": save_created_ticket_response.success}, "status": 200}

            self._logger.info(f'Got response saving created ticket feedback from Konstellation: {response["body"]}')

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error saving created ticket feedback from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f'Got error saving created tickets feedback from Konstellation: {response["body"]}')

        return response

    async def save_closed_ticket_feedback(self, payload: dict) -> dict:
        try:
            stub = await self._create_stub()
            save_closed_ticket_response = await stub.SaveClosedTicketsFeedback(
                Parse(
                    json.dumps(payload).encode("utf8"),
                    pb2.SaveClosedTicketsFeedbackRequest(),
                    ignore_unknown_fields=False,
                ),
                timeout=120,
            )

            response = {"body": {"success": save_closed_ticket_response.success}, "status": 200}

            self._logger.info(f'Got response saving closed ticket feedback from Konstellation: {response["body"]}')

        except grpc.RpcError as grpc_e:
            response = {
                "body": f"Grpc error details: {grpc_e.details()}",
                "status": self.__grpc_to_http_status(grpc_e.code()),
            }
            self._logger.error(f'Got grpc error saving closed ticket feedback from Konstellation: {response["body"]}')

        except Exception as e:
            response = {"body": f"Error: {e.args[0]}", "status": 500}
            self._logger.error(f'Got error saving closed tickets feedback from Konstellation: {response["body"]}')

        return response
