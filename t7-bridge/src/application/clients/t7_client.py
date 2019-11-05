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
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        def get_prediction():
            self._logger.info(f'Getting prediction for ticket id: {ticket_id}')

            response = requests.get(f"{self._config.T7CONFIG['base_url']}api/v1/suggestions?ticketId={ticket_id}",
                                    headers=self._get_request_headers(),
                                    verify=False)

            if response.status_code in range(200, 299):
                return response.json()['assets']
            else:
                raise Exception

        return get_prediction()
