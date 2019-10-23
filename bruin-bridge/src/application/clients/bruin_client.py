import base64
from tenacity import retry, wait_exponential, stop_after_delay

import requests


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
        def get_all_tickets(client_id, ticket_id, ticket_status, category, ticket_topic):
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

        return get_all_tickets(client_id, ticket_id, ticket_status, category, ticket_topic)

    def get_ticket_details(self, ticket_id):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def get_ticket_details(ticket_id):
            self._logger.info(f'Getting ticket details for ticket id: {ticket_id}')
            response = requests.get(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details',
                                    headers=self._get_request_headers(),
                                    verify=False)

            if response.status_code in range(200, 299):
                return response.json()
            else:
                self.login()
                raise Exception
        return get_ticket_details(ticket_id)

    def post_ticket_note(self, ticket_id, ticket_note):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def post_ticket_note(ticket_id, ticket_note):
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
        return post_ticket_note(ticket_id, ticket_note)

    def post_ticket(self, client_id, category, services, notes, contacts):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']))
        def post_ticket(client_id, category, services, notes, contacts):
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
        return post_ticket(client_id, category, services, notes, contacts)
