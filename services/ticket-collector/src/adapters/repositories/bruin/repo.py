import base64
import datetime
import requests


class BruinRepository:
    def __init__(self, logger, config):
        self._logger = logger
        self._config = config
        self._token = None
        self.login()

    def login(self):
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

            self._token = bearer_token
        except Exception as e:
            self._logger.info('An error occurred while trying to login to Bruin')

    def request_tickets_by_date_range(self, start: datetime, end: datetime) -> list:
        """
        Request tickets by date range.
        :param start:
        :param end:
        :return list:
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

        if tickets_response.status_code in range(200, 300):
            self._logger.info(f'Got bruin tickets between {start} and {end}')
            return tickets_response.json()['responses']
        elif tickets_response.status_code == 401:
            self._logger.warning('Bruin token expired, re-logging in...')
            self.login()
            return self.request_tickets_by_date_range(start, end)
        else:
            self._logger.error(f'Failed to get bruin tickets between {start} and {end}. '
                               f'Status code: {tickets_response.status_code}')
            return []

    def request_ticket_events(self, ticket_id: str) -> list:
        """
        Request ticket events
        :param ticket_id:
        :return list:
        """
        endpoint = 'https://api.bruin.com/api/Ticket/AITicketData'

        headers = {
            'Authorization': 'Bearer %s' % self._token
        }

        params = {
            'ticketId': ticket_id
        }

        self._logger.info(f'Requesting bruin ticket events for ticket {ticket_id}')
        tickets_detail_response = requests.get(endpoint, params=params, headers=headers, verify=False)

        if tickets_detail_response.status_code in range(200, 300):
            self._logger.info(f'Got bruin ticket events for ticket {ticket_id}')
            return tickets_detail_response.json()['result']
        elif tickets_detail_response.status_code == 401:
            self._logger.warning('Bruin token expired, re-logging in...')
            self.login()
            return self.request_ticket_events(ticket_id)
        else:
            self._logger.error(f'Failed to get bruin ticket events for ticket {ticket_id}. '
                               f'Status code: {tickets_detail_response.status_code}')
            return []
