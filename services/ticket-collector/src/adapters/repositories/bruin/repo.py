import base64
import datetime
import requests
from typing import Dict


class BruinRepository:
    def __init__(self, logger, config):
        self._logger = logger
        self._config = config
        self._token = self.login()

    def login(self) -> str:
        login_credentials = ('%s:%s' % (self._config['bruin']['id'], self._config['bruin']['secret']))
        login_credentials = login_credentials.encode()
        login_credentials_b64 = base64.b64encode(login_credentials).decode()

        headers = {
            'authorization': ('Basic %s' % login_credentials_b64),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        form_data = {
            'grant_type': 'client_credentials',
            'scope': 'public_api'
        }

        try:
            response = requests.post(
                'https://id.bruin.com/identity/connect/token',
                data=form_data,
                headers=headers,
            )
            bearer_token = response.json()['access_token']
            self._logger.info('Logged into Bruin!')

            return bearer_token
        except Exception as err:
            self._logger.info('An error occurred while trying to login to Bruin.')

    def request_tickets_by_date_range(self, start: datetime, end: datetime) -> Dict:
        """
        Request tickets by date range.
        :param start:
        :param end:
        :return Dict:
        """
        endpoint = 'https://api.bruin.com/api/Ticket/basic'

        headers = {
            'Authorization': 'Bearer %s' % self._token
        }

        params = {
            'StartDate': start,
            'EndDate': end,
            'TicketTopic': 'VOO'
        }

        self._logger.info(f'Requesting bruin tickets between {start} and {end}')

        tickets_response = requests.get(endpoint, params=params, headers=headers, verify=False)

        self._logger.info(f'Got bruin tickets response with status {tickets_response.status_code}')

        if tickets_response.status_code != 200:
            self._logger.info(tickets_response.json())

        return tickets_response.json()['responses']

    def request_ticket_events(self, ticket_id: str) -> Dict:
        """
        Request ticket events
        :param ticket_id:
        :return Dict:
        """
        endpoint = 'https://api.bruin.com/api/Ticket/AITicketData'

        headers = {
            'Authorization': 'Bearer %s' % self._token
        }

        params = {
            'ticketId': ticket_id
        }

        tickets_detail_response = requests.get(endpoint, params=params, headers=headers, verify=False)
        # self._logger.info(tickets_detail_response)
        return tickets_detail_response.json()['result']
