import base64
import json

import humps
import requests
from tenacity import retry, wait_exponential, stop_after_delay


class BruinClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger
        self._bearer_token = ""

    def login(self):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def login():
            self._logger.info("Logging into Bruin...")
            creds = str.encode(self._config.BRUIN_CONFIG["client_id"] + ":" + self._config.BRUIN_CONFIG["client_secret"]
                               )
            headers = {
                "authorization": f"Basic {base64.b64encode(creds).decode()}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            form_data = {
                "grant_type": "client_credentials",
                "scope": "public_api"
            }

            try:
                response = requests.post(f'{self._config.BRUIN_CONFIG["login_url"]}/identity/connect/token',
                                         data=form_data,
                                         headers=headers)
                self._bearer_token = response.json()["access_token"]
                self._logger.info("Logged into Bruin!")

            except Exception as err:
                self._logger.error("An error occurred while trying to login to Bruin")
                self._logger.error(f"{err}")

        login()

    def _get_request_headers(self):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        headers = {
            "authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
        return headers

    def get_all_tickets(self, client_id, ticket_id, ticket_status, category, ticket_topic):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def get_all_tickets():
            self._logger.info(f'Getting all tickets for client id: {client_id}')

            params = {
                "ClientId": client_id,
                "TicketId": ticket_id,
                "TicketStatus": ticket_status,
                "Category": category,
                "TicketTopic": ticket_topic
            }
            response = requests.get(f"{self._config.BRUIN_CONFIG['base_url']}/api/Ticket",
                                    headers=self._get_request_headers(),
                                    verify=False, params=params)

            if response.status_code in range(200, 299):
                return response.json()['responses']
            else:
                self.login()
                raise Exception

        return get_all_tickets()

    def get_ticket_details(self, ticket_id):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def get_ticket_details():
            self._logger.info(f'Getting ticket details for ticket id: {ticket_id}')
            response = requests.get(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details',
                                    headers=self._get_request_headers(),
                                    verify=False)

            if response.status_code in range(200, 299):
                return response.json()
            else:
                self.login()
                raise Exception

        return get_ticket_details()

    def post_ticket_note(self, ticket_id, ticket_note):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def post_ticket_note():
            self._logger.info(f'Getting posting notes for ticket id: {ticket_id}')
            payload = {
                "note": ticket_note
            }
            response = requests.post(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes',
                                     headers=self._get_request_headers(),
                                     json=payload,
                                     verify=False)

            if response.status_code in range(200, 299):
                return response.json()
            else:
                self.login()
                raise Exception

        return post_ticket_note()

    def post_ticket(self, client_id, category, services, notes, contacts):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def post_ticket():
            self._logger.info(f'Posting note for client id:{client_id}')
            payload = {
                "clientId": client_id,
                "category": category,
                "services": services,
                "notes": notes,
                "contacts": contacts
            }
            response = requests.post(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/',
                                     headers=self._get_request_headers(),
                                     json=payload,
                                     verify=False)

            if response.status_code in range(200, 299):
                return response.json()
            else:
                self.login()
                raise Exception

        return post_ticket()

    def update_ticket_status(self, ticket_id, detail_id, ticket_status):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def update_ticket_status():
            self._logger.info(f'Updating ticket status for ticket id: {ticket_id}')

            payload = {
                "Status": ticket_status
            }
            response = requests.put(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details'
                                    f'/{detail_id}/status',
                                    headers=self._get_request_headers(),
                                    json=payload,
                                    verify=False)
            if response.status_code in range(200, 299):
                return response.json()
            else:
                self.login()
                raise Exception

        return update_ticket_status()

    def get_management_status(self, filters):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def get_management_status():
            self._logger.info(f'Getting management status for client ID: {filters["client_id"]}')
            parsed_filters = humps.pascalize(filters)
            self._logger.info(f'Filters that will be applied (parsed to PascalCase): {json.dumps(parsed_filters)}')

            response = requests.get(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                                    headers=self._get_request_headers(),
                                    params=parsed_filters,
                                    verify=False)

            if response.status_code in range(200, 299):
                return response.json()

            if response.status_code == 400:
                return 400

            if response.status_code == 401:
                self.login()
                raise Exception

            if response.status_code in range(500, 511):
                raise Exception

        return get_management_status()
