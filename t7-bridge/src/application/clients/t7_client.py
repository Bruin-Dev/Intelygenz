import requests
from tenacity import retry, wait_exponential, stop_after_delay


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

    def get_prediction(self, ticket_id):
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
                return_response["body"] = f'Got 403 Forbidden from TNBA API'
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

        try:
            return get_prediction()
        except Exception as e:
            return e.args[0]
