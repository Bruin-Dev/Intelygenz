import requests
import json
from tenacity import retry, wait_exponential, stop_after_delay
import grpc
from google.protobuf.json_format import Parse
from application.clients import public_input_pb2 as pb2
from application.clients import public_input_pb2_grpc as pb2_grpc


class T7Client:

    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

    def _get_request_headers(self):
        headers = {
            'X-Client-Name': self._config.T7CONFIG['client_name'],
            'X-Client-Version': self._config.T7CONFIG['version'],
            'X-Auth-Token': self._config.T7CONFIG['auth-token']
        }
        return headers

    def get_prediction(self, ticket_id, ticket_rows):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']), reraise=True)
        def get_prediction():
            self._logger.info(f'Getting prediction for ticket id: {ticket_id}')

            try:
                response = requests.get(f"{self._config.T7CONFIG['base_url']}/api/v1/suggestions?ticketId={ticket_id}",
                                        headers=self._get_request_headers(),
                                        verify=True)
            except requests.exceptions.ConnectionError as conn_err:
                self._logger.error(f'Got connection error from T7 client {conn_err}')
                raise Exception({"body": conn_err, "status": 500})

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                self._logger.info(f'Got response from T7: {response.json()}')
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from TNBA API: {response.json()}")

            if response.status_code == 401:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got unauthorized from TNBA API: {response.json()}")

            if response.status_code == 403:
                # TNBA API doesn't return a JSON when 403, but a doc, so we put our own message
                return_response["body"] = 'Got 403 Forbidden from TNBA API'
                return_response["status"] = response.status_code
                self._logger.error(f"Got 403 Forbidden from TNBA API")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got possible 404 as 500 from TNBA API: {response.json()}")
                return_response["body"] = f"Got possible 404 as 500 from TNBA API: {response.json()}"
                return_response["status"] = 500
                # TNBA API returns 500 code if ticketId is not found in Bruin. We bypass that here
                # by using the error message under the "error" key in the response body
                if response.json().get("error") and not response.json()["error"] in "error_getting_ticket_data":
                    self._logger.error(f"Got unknown 500 error from TNBA API {response.status_code}. Retrying...")
                    return_response["body"] = f"Got 500 from TNBA API: {response.json()}"
                    raise Exception(return_response)
            return return_response

        def get_kre_prediction():
            try:
                credentials = grpc.ssl_channel_credentials()
                c = grpc.secure_channel(f"{self._config.KRE_CONFIG['base_url']}", credentials=credentials)

                stub = pb2_grpc.EntrypointStub(c)

                request = pb2.PredictionRequest()
                request.ticket_id = ticket_id
                for row in ticket_rows:
                    ticket_row = Parse(json.dumps(row), pb2.TicketRow())
                    request.ticket_rows.append(ticket_row)

                save_prediction_response = stub.Prediction(request)
                kre_response = {
                    "body": save_prediction_response.message,
                    "status_code": "SUCCESS"
                }

                self._logger.info(f'Got response getting predictions from KRE: {kre_response["body"]}')

            except grpc.RpcError as kre_e:
                kre_response = {
                    "body": f"Error details for {kre_e.code()}: {kre_e.details}",
                    "status_code": f"{kre_e.code()}"
                }
                self._logger.error(f'Got error getting predictions from KRE: {kre_response["body"]}')
                pass

            except Exception as kre_e:
                kre_response = {
                    "body": f"Error: {kre_e.args[0]}",
                    "status_code": "UNKNOWN_ERROR"
                }
                self._logger.error(f'Got error getting predictions from KRE: {kre_response["body"]}')
                pass

            return kre_response

        try:
            t7_response = get_prediction()
            kre_response = get_kre_prediction()
            t7_response["kre_response"] = kre_response
            return t7_response
        except Exception as e:
            return e.args[0]

    def post_automation_metrics(self, params):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']), reraise=True)
        def post_automation_metrics():
            self._logger.info(f'Posting params of: {params} as automation metrics')

            try:
                response = requests.post(f"{self._config.T7CONFIG['base_url']}/api/v2/metrics",
                                         headers=self._get_request_headers(),
                                         json=params,
                                         verify=True)
            except requests.exceptions.ConnectionError as conn_err:
                self._logger.error(f'Got connection error from T7 client {conn_err}')
                raise Exception({"body": conn_err, "status": 500})

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                self._logger.info(f'Got response from T7: {response.status_code}')
                return_response["body"] = "Successfully posted metrics"
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from TNBA API: {response.json()}")

            if response.status_code == 401:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got unauthorized from TNBA API: {response.json()}")

            if response.status_code == 403:
                # TNBA API doesn't return a JSON when 403, but a doc, so we put our own message
                return_response["body"] = 'Got 403 Forbidden from TNBA API'
                return_response["status"] = response.status_code
                self._logger.error(f"Got 403 Forbidden from TNBA API")
            if response.status_code in range(500, 513):
                self._logger.error(f"Got possible 404 as 500 from TNBA API: {response.json()}")
                return_response["body"] = f"Got possible 404 as 500 from TNBA API: {response.json()}"
                return_response["status"] = 500
                # TNBA API returns 500 code if ticketId is not found in Bruin. We bypass that here
                # by using the error message under the "error" key in the response body
                if response.json().get("error") and not response.json()["error"] in "error_getting_ticket_data":
                    self._logger.error(f"Got unknown 500 error from TNBA API {response.status_code}. Retrying...")
                    return_response["body"] = f"Got 500 from TNBA API: {response.json()}"
                    raise Exception(return_response)
            return return_response

        def post_kre_automation_metrics():

            try:
                credentials = grpc.ssl_channel_credentials()
                c = grpc.secure_channel(f"{self._config.KRE_CONFIG['base_url']}", credentials=credentials)

                stub = pb2_grpc.EntrypointStub(c)

                request = pb2.SaveMetricsRequest()
                request.ticket_id = params['ticket_id']
                for row in params['camel_ticket_rows']:
                    ticket_row = Parse(json.dumps(row), pb2.TicketRow())
                    request.ticket_rows.append(ticket_row)

                save_metrics_response = stub.SaveMetrics(request)
                kre_response = {
                    "body": save_metrics_response.message,
                    "status_code": "SUCCESS"
                }

                self._logger.info(f'Got response saving metrics from KRE: {kre_response["body"]}')

            except grpc.RpcError as kre_e:
                kre_response = {
                    "body": f"Error details for {kre_e.code()}: {kre_e.details}",
                    "status_code": f"{kre_e.code()}"
                }
                self._logger.error(f'Got error saving metrics from KRE: {kre_response["body"]}')
                pass

            except Exception as kre_e:
                kre_response = {
                    "body": f"Error: {kre_e.args[0]}",
                    "status_code": "UNKNOWN_ERROR"
                }
                self._logger.error(f'Got error saving metrics from KRE: {kre_response["body"]}')
                pass

            return kre_response

        try:
            t7_response = post_automation_metrics()
            kre_response = post_kre_automation_metrics()
            t7_response["kre_response"] = kre_response
            return t7_response
        except Exception as e:
            return e.args[0]
