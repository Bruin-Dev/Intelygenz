import base64
import datetime
import httpx


class BruinRepository:
    def __init__(self, logger, config):
        self._logger = logger
        self._config = config
        self._token = None
        self.login()

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self._token}'
        }

    def login(self):
        login_credentials = f"{self._config['bruin']['id']}:{self._config['bruin']['secret']}"
        login_credentials = login_credentials.encode()
        login_credentials_b64 = base64.b64encode(login_credentials).decode()

        headers = {
            'Authorization': f'Basic {login_credentials_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        form_data = {
            'grant_type': 'client_credentials',
            'scope': 'public_api'
        }

        try:
            response = httpx.post(
                'https://id.bruin.com/identity/connect/token',
                data=form_data,
                headers=headers,
            )
            self._token = response.json()['access_token']
            self._logger.info('Logged into bruin!')
        except Exception as e:
            self._logger.info(f'Failed to log into bruin. Error: {e}')

    async def request_tickets_by_date_range(self, start: datetime, end: datetime) -> list:
        """
        Request tickets by date range.
        :param start:
        :param end:
        :return list:
        """
        async with httpx.AsyncClient() as client:
            try:
                self._logger.info(f'Requesting bruin tickets between {start} and {end}')

                params = {
                    'StartDate': start,
                    'EndDate': end,
                    'TicketTopic': 'VOO',
                }

                tickets_response = await client.get(
                    'https://api.bruin.com/api/Ticket/basic',
                    params=params,
                    headers=self.get_headers(),
                    timeout=90,
                )

                if tickets_response.status_code in range(200, 300):
                    self._logger.info(f'Got bruin tickets between {start} and {end}')
                    return tickets_response.json()['responses']
                elif tickets_response.status_code == 401:
                    self._logger.warning('Bruin token expired, re-logging in...')
                    self.login()
                    return await self.request_tickets_by_date_range(start, end)
                else:
                    self._logger.error(f'Failed to get bruin tickets between {start} and {end}. '
                                       f'Status code: {tickets_response.status_code}')
                    return []
            except Exception as e:
                self._logger.error(f'Failed to get bruin tickets between {start} and {end}. Error: {e}')
                return []

    async def request_ticket_events(self, ticket_id: str) -> list:
        """
        Request ticket events
        :param ticket_id:
        :return list:
        """
        async with httpx.AsyncClient() as client:
            try:
                self._logger.info(f'Requesting bruin ticket events for ticket {ticket_id}')

                params = {
                    'ticketId': ticket_id,
                }

                tickets_detail_response = await client.get(
                    'https://api.bruin.com/api/Ticket/AITicketData',
                    params=params,
                    headers=self.get_headers(),
                    timeout=90,
                )

                if tickets_detail_response.status_code in range(200, 300):
                    self._logger.info(f'Got bruin ticket events for ticket {ticket_id}')
                    return tickets_detail_response.json()['result']
                elif tickets_detail_response.status_code == 401:
                    self._logger.warning('Bruin token expired, re-logging in...')
                    self.login()
                    return await self.request_ticket_events(ticket_id)
                else:
                    self._logger.error(f'Failed to get bruin ticket events for ticket {ticket_id}. '
                                       f'Status code: {tickets_detail_response.status_code}')
                    return []
            except Exception as e:
                self._logger.error(f'Failed to get bruin ticket events for ticket {ticket_id}. Error: {e}')
                return []
