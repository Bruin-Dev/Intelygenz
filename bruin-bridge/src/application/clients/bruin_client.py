import base64
import json

import aiohttp
import humps


class BruinClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._bearer_token = ""
        self._session = aiohttp.ClientSession()

    async def login(self):
        self._logger.info("Logging into Bruin...")
        login_credentials = f'{self._config.BRUIN_CONFIG["client_id"]}:{self._config.BRUIN_CONFIG["client_secret"]}'
        login_credentials = login_credentials.encode()
        login_credentials_b64 = base64.b64encode(login_credentials).decode()

        headers = {
            "authorization": f"Basic {login_credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form_data = {
            "grant_type": "client_credentials",
            "scope": "public_api"
        }

        try:
            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["login_url"]}/identity/connect/token',
                data=form_data,
                headers=headers,
            )

            self._bearer_token = (await response.json())["access_token"]
            self._logger.info("Logged into Bruin!")
        except Exception as err:
            self._logger.error("An error occurred while trying to login to Bruin")
            self._logger.error(f"{err}")

    def _get_request_headers(self):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        headers = {
            "authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
        return headers

    async def get_all_tickets(self, params):
        try:
            if params.get("category"):
                params["product_category"] = params["category"]
                del(params["category"])

            parsed_params = humps.pascalize(params)

            self._logger.info(f'Getting ticket(s) using params {json.dumps(parsed_params)}')

            response = await self._session.get(
                f"{self._config.BRUIN_CONFIG['base_url']}/api/Ticket",
                params=parsed_params,
                headers=self._get_request_headers(),
                ssl=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json['responses']
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resource not found for params {parsed_params}")
                return_response["body"] = "Resource not found"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response
        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def get_ticket_details(self, ticket_id):
        try:
            self._logger.info(f'Getting ticket details for ticket id: {ticket_id}')

            response = await self._session.get(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details',
                headers=self._get_request_headers(),
                ssl=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resource not found for ticket id {ticket_id}")
                return_response["body"] = "Resource not found"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def post_ticket_note(self, ticket_id, payload):
        try:
            self._logger.info(f'Getting posting notes for ticket id: {ticket_id}')

            self._logger.info(f'Payload that will be applied: {json.dumps(payload)}')

            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes',
                json=payload,
                headers=self._get_request_headers(),
                ssl=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for ticket_id {ticket_id} with "
                                   f"payload {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def post_multiple_ticket_notes(self, ticket_id, payload):
        try:
            self._logger.info(f'Posting multiple notes for ticket id: {ticket_id}. Payload {json.dumps(payload)}')

            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.post(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                    json=payload,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. Cause: {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resources not posted for ticket_id {ticket_id} with "
                                   f"payload {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def post_ticket(self, payload):
        try:
            self._logger.info(f'Posting ticket for client id:{payload["clientId"]}')
            self._logger.info(f'Payload that will be applied : {json.dumps(payload, indent=2)}')

            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/',
                json=payload,
                headers=self._get_request_headers(),
                ssl=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def update_ticket_status(self, ticket_id, detail_id, payload):
        try:
            self._logger.info(f'Updating ticket status for ticket id: {ticket_id}')

            self._logger.info(f'Payload that will be applied (parsed to PascalCase): {json.dumps(payload)}')

            response = await self._session.put(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/{detail_id}/status',
                json=payload,
                headers=self._get_request_headers(),
                ssl=False,
            )
            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                self._logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def get_management_status(self, filters):
        try:
            self._logger.info(f'Getting management status for client ID: {filters["client_id"]}')
            parsed_filters = humps.pascalize(filters)
            self._logger.info(f'Filters that will be applied (parsed to PascalCase): {json.dumps(parsed_filters)}')
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                    params=parsed_filters,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = f"Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def post_outage_ticket(self, client_id, service_number):
        try:
            self._logger.info(
                f'Posting outage ticket for client with ID {client_id} and for service number {service_number}'
            )

            payload = {
                "ClientID": client_id,
                "WTNs": [service_number],
                "RequestDescription": "Automation Engine -- Service Outage Trouble"
            }
            self._logger.info(f'Posting payload {json.dumps(payload)} to create new outage ticket...')

            return_response = dict.fromkeys(["body", "status"])
            url = f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'

            try:
                response = await self._session.post(url, json=payload, headers=self._get_request_headers(), ssl=False)
            except aiohttp.ClientConnectionError as err:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. Cause: {err}")
                return_response["body"] = f"Connection error in Bruin API. Cause: {err}"
                return_response["status"] = 500
                return return_response

            status_code = response.status
            if status_code in range(200, 300):
                response_json = await response.json()
                # The root key may differ depending on the status code...
                ticket_data = response_json.get(
                    'assets',
                    response_json.get('items')
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
                return_response["status"] = status_code

            if status_code == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = status_code
                self._logger.error(
                    f"Got HTTP 400 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    f"Reason: {response_json}"
                )

            if status_code == 401:
                self._logger.info("Got HTTP 401 from Bruin.")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if status_code == 403:
                return_response["body"] = ("Permissions to create a new outage ticket with payload "
                                           f"{json.dumps(payload)} were not granted")
                return_response["status"] = status_code
                self._logger.error(
                    "Got HTTP 403 from Bruin. Bruin client doesn't have permissions to post a new outage ticket with "
                    f"payload {json.dumps(payload)}"
                )

            if status_code == 404:
                self._logger.error(
                    f"Got HTTP 404 from Bruin when posting outage ticket. Payload: {json.dumps(payload)}"
                )
                return_response["body"] = f"Check mistypings in URL: {url}"
                return_response["status"] = status_code

            if status_code in range(500, 514):
                self._logger.error(
                    f"Got HTTP {status_code} from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                )
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def get_client_info(self, filters):
        try:
            self._logger.info(f'Getting Bruin client ID for filters: {filters}')
            parsed_filters = humps.pascalize(filters)
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                    params=parsed_filters,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                return_response["body"] = f"Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def change_detail_work_queue(self, ticket_id, filters):
        try:
            self._logger.info(f'Changing work queue for ticket detail: {filters} and ticket id : {ticket_id}')
            response = await self._session.put(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                json=filters,
                headers=self._get_request_headers(),
                ssl=False)
            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 299):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.info(f'Work queue changed for ticket detail: {filters}')

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = f"Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def get_possible_detail_next_result(self, ticket_id, filters):
        try:
            self._logger.info(f'Getting work queues for ticket detail: {filters}')
            response = await self._session.get(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                params=filters,
                headers=self._get_request_headers(),
                ssl=False,
            )
            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 299):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.info(f'Got possible next work queue results for : {filters}')

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = f"Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }

    async def get_ticket_task_history(self, filters):
        try:
            self._logger.info(f'Getting ticket task history for ticket: {filters}')
            return_response = dict.fromkeys(["body", "status"])
            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filters["ticket_id"]}',
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                self._logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.info(f'Got ticket task history for : {filters}')

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                self._logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                self._logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from Bruin"
                return_response["status"] = response.status

            if response.status in range(500, 513):
                self._logger.error(f"Got {response.status}.")
                return_response["body"] = "Got internal error from Bruin"
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }
