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

    def get_all_tickets(self, params):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def get_all_tickets():
            self._logger.info(f'Getting all tickets for client id: {params["client_id"]}')

            parsed_params = humps.pascalize(params)

            self._logger.info(f'Params that will be applied (parsed to PascalCase): {json.dumps(parsed_params)}')

            response = requests.get(f"{self._config.BRUIN_CONFIG['base_url']}/api/Ticket",
                                    headers=self._get_request_headers(),
                                    verify=False, params=parsed_params)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()['responses']
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Bruin, re-login and retrying getting tickets")
                self.login()
                return_response["body"] = f"Maximum retries while relogin"
                return_response["status"] = response.status_code
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Bruin, resource not found for params {parsed_params}")
                return_response["body"] = "Resource not found"
                return_response["status"] = response.status_code

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response
        try:
            return get_all_tickets()
        except Exception as e:
            return e.args[0]

    def get_ticket_details(self, ticket_id):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def get_ticket_details():
            self._logger.info(f'Getting ticket details for ticket id: {ticket_id}')
            response = requests.get(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details',
                                    headers=self._get_request_headers(),
                                    verify=False)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Bruin, re-login and retrying getting ticket details")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = response.status_code
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Bruin, resource not found for ticket id {ticket_id}")
                return_response["body"] = "Resource not found"
                return_response["status"] = response.status_code

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_ticket_details()
        except Exception as e:
            return e.args[0]

    def post_ticket_note(self, ticket_id, payload):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def post_ticket_note():
            self._logger.info(f'Getting posting notes for ticket id: {ticket_id}')

            self._logger.info(f'Payload that will be applied: {json.dumps(payload)}')

            response = requests.post(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes',
                                     headers=self._get_request_headers(),
                                     json=payload,
                                     verify=False)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Bruin, re-login and retrying posting ticket note")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for ticket_id {ticket_id} with "
                                   f"payload {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return post_ticket_note()
        except Exception as e:
            return e.args[0]

    def post_ticket(self, payload):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def post_ticket():
            self._logger.info(f'Posting ticket for client id:{payload["clientId"]}')
            self._logger.info(f'Payload that will be applied : {json.dumps(payload, indent=2)}')

            response = requests.post(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/',
                                     headers=self._get_request_headers(),
                                     json=payload,
                                     verify=False)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Bruin, re-login and retrying posting ticket")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return post_ticket()
        except Exception as e:
            return e.args[0]

    def update_ticket_status(self, ticket_id, detail_id, payload):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def update_ticket_status():
            self._logger.info(f'Updating ticket status for ticket id: {ticket_id}')

            self._logger.info(f'Payload that will be applied (parsed to PascalCase): {json.dumps(payload)}')

            response = requests.put(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details'
                                    f'/{detail_id}/status',
                                    headers=self._get_request_headers(),
                                    json=payload,
                                    verify=False)
            return_response = dict.fromkeys(["body", "status_code"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Bruin, re-login and retrying updating ticket status")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return update_ticket_status()
        except Exception as e:
            return e.args[0]

    def get_management_status(self, filters):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def get_management_status():
            self._logger.info(f'Getting management status for client ID: {filters["client_id"]}')
            parsed_filters = humps.pascalize(filters)
            self._logger.info(f'Filters that will be applied (parsed to PascalCase): {json.dumps(parsed_filters)}')
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = requests.get(f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                                        headers=self._get_request_headers(),
                                        params=parsed_filters,
                                        verify=False)
            except ConnectionError as e:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                raise Exception(return_response)

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Bruin {response.json()}")

            if response.status_code == 401:
                self._logger.info(f"Got 401 from Bruin, re-login and retrying get management status")
                self.login()
                return_response["body"] = f"Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 403:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Forbidden error from Bruin {response.json()}")

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = f"Got internal error from Bruin"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_management_status()
        except Exception as e:
            return e.args[0]

    def post_outage_ticket(self, client_id, service_number):
        @retry(wait=wait_exponential(multiplier=self._config.BRUIN_CONFIG['multiplier'],
                                     min=self._config.BRUIN_CONFIG['min']),
               stop=stop_after_delay(self._config.BRUIN_CONFIG['stop_delay']), reraise=True)
        def post_outage_ticket():
            self._logger.info(
                f'Posting outage ticket for client with ID {client_id} and for service number {service_number}'
            )

            payload = {
                "ClientID": client_id,
                "WTNs": [service_number],
                "RequestDescription": "Automation Engine -- Service Outage Trouble"
            }
            self._logger.info(f'Posting payload {json.dumps(payload)} to create new outage ticket...')

            return_response = dict.fromkeys(["body", "status_code"])
            url = f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'

            try:
                response = requests.post(url, headers=self._get_request_headers(),
                                         json=payload, verify=False)
            except ConnectionError as err:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. Cause: {err}")
                return_response["body"] = f"Connection error in Bruin API. Cause: {err}"
                return_response["status_code"] = 500
                raise Exception(return_response)

            status_code = response.status_code
            if status_code in range(200, 300):
                # The root key may differ depending on the status code...
                ticket_data = response.json().get(
                    'assets',
                    response.json().get('items')
                )[0]

                # HTTP 409 means the service number is already under an in-progress ticket
                # HTTP 471 means the service number is already under a resolved ticket
                # These two codes are embedded in the body of a HTTP 200 response
                if ticket_data['errorCode'] == 409:
                    self._logger.info(
                        f"Got HTTP 409 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with In-Progress status"
                    )
                    status_code = 409
                elif ticket_data['errorCode'] == 471:
                    self._logger.info(
                        f"Got HTTP 471 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status"
                    )
                    status_code = 471

                return_response["body"] = ticket_data
                return_response["status_code"] = status_code

            if status_code == 400:
                return_response["body"] = response.json()
                return_response["status_code"] = status_code
                self._logger.error(
                    f"Got HTTP 400 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    f"Reason: {response.json()}"
                )

            if status_code == 401:
                self._logger.info(
                    "Got HTTP 401 from Bruin. Re-login and trying to post outage ticket again with payload "
                    f"{json.dumps(payload)}"
                )
                self.login()
                return_response["body"] = "Maximum retries reached while re-login"
                return_response["status_code"] = status_code
                raise Exception(return_response)

            if status_code == 403:
                return_response["body"] = ("Permissions to create a new outage ticket with payload "
                                           f"{json.dumps(payload)} were not granted")
                return_response["status_code"] = status_code
                self._logger.error(
                    "Got HTTP 403 from Bruin. Bruin client doesn't have permissions to post a new outage ticket with "
                    f"payload {json.dumps(payload)}"
                )

            if status_code == 404:
                self._logger.error(
                    f"Got HTTP 404 from Bruin when posting outage ticket. Payload: {json.dumps(payload)}"
                )
                return_response["body"] = f"Check mistypings in URL: {url}"
                return_response["status_code"] = status_code

            if status_code in range(500, 514):
                self._logger.error(
                    f"Got HTTP {status_code} from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    "Retrying request..."
                )
                return_response["body"] = "Got internal error from Bruin"
                return_response["status_code"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return post_outage_ticket()
        except Exception as e:
            return e.args[0]
