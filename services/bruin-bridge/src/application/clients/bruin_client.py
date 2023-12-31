import base64
import json
import logging
from http import HTTPStatus
from typing import Dict

import aiohttp
import humps
from application.clients.bruin_session import BruinGetRequest, BruinResponse, BruinSession

logger = logging.getLogger(__name__)

BRUIN_401_RESPONSE = "Got 401 from Bruin"
BRUIN_404_RESPONSE = "Resource not found"
BRUIN_500_RESPONSE = "Got internal error from Bruin"


class BruinClient:
    def __init__(self, config):
        self._config = config

        self._bearer_token = ""

    async def create_session(self):
        self._session = aiohttp.ClientSession(trace_configs=self._config.AIOHTTP_CONFIG["tracers"])
        self._bruin_session = BruinSession(session=self._session, base_url=self._config.BRUIN_CONFIG["base_url"])

    async def login(self):
        logger.info("Logging into Bruin...")
        login_credentials = f'{self._config.BRUIN_CONFIG["client_id"]}:{self._config.BRUIN_CONFIG["client_secret"]}'
        login_credentials = login_credentials.encode()
        login_credentials_b64 = base64.b64encode(login_credentials).decode()

        headers = {
            "authorization": f"Basic {login_credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        form_data = {"grant_type": "client_credentials", "scope": "public_api"}

        try:
            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["login_url"]}/identity/connect/token',
                data=form_data,
                headers=headers,
            )

            self._bearer_token = (await response.json())["access_token"]
            self._bruin_session.access_token = self._bearer_token
            logger.info("Logged into Bruin!")
        except Exception as err:
            logger.error(f"An error occurred while trying to login to Bruin: {err}")

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

            parsed_params = humps.pascalize(params)

            logger.info(f"Getting ticket(s) using params {json.dumps(parsed_params)}")

            response = await self._session.get(
                f"{self._config.BRUIN_CONFIG['base_url']}/api/Ticket",
                params=parsed_params,
                headers=self._get_request_headers(),
                ssl=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json["responses"]
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not found for params {parsed_params}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response
        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_tickets_basic_info(self, params: dict) -> dict:
        return_response = dict.fromkeys(["body", "status"])

        request_params = humps.pascalize(params)

        logger.info(f"Getting tickets basic info using params {json.dumps(request_params)}...")

        try:
            response = await self._session.get(
                f"{self._config.BRUIN_CONFIG['base_url']}/api/Ticket/basic",
                params=request_params,
                headers=self._get_request_headers(),
                ssl=False,
            )
        except aiohttp.ClientConnectionError as e:
            logger.error(f"A connection error happened while trying to connect to Bruin API: {e}")
            return_response["body"] = f"Connection error in Bruin API. Cause: {e}"
            return_response["status"] = 500
            return return_response

        if response.status in range(200, 300):
            logger.info(f"Got HTTP 200 from GET /api/Ticket/basic for params {json.dumps(request_params)}")
            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = response.status

        if response.status == 400:
            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = response.status
            logger.error(f"Got error from Bruin {response_json}")

        if response.status == 401:
            logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.login()
            return_response["body"] = BRUIN_401_RESPONSE
            return_response["status"] = response.status

        if response.status == 403:
            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = response.status
            logger.error(f"Forbidden error from Bruin {response_json}")

        if response.status == 404:
            logger.error(f"Got 404 from Bruin, resource not found for params {request_params}")
            return_response["body"] = BRUIN_404_RESPONSE
            return_response["status"] = response.status

        if response.status in range(500, 513):
            logger.error(f"Got {response.status}.")
            return_response["body"] = BRUIN_500_RESPONSE
            return_response["status"] = 500

        return return_response

    async def get_ticket_details(self, ticket_id):
        try:
            logger.info(f"Getting ticket details for ticket id: {ticket_id}")

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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not found for ticket id {ticket_id}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_ticket_note(self, ticket_id, payload):
        try:
            logger.info(f"Getting posting notes for ticket id: {ticket_id}")

            logger.info(f"Payload that will be applied: {json.dumps(payload)}")

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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(
                    f"Got 404 from Bruin, resource not posted for ticket_id {ticket_id} with payload {payload}"
                )
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_multiple_ticket_notes(self, ticket_id, payload):
        try:
            logger.info(f"Posting multiple notes for ticket id: {ticket_id}. Payload {json.dumps(payload)}")

            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.post(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                    json=payload,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(
                    f"Got 404 from Bruin, resources not posted for ticket_id {ticket_id} with payload {payload}"
                )
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_ticket(self, payload):
        try:
            logger.info(f'Posting ticket for client id:{payload["clientId"]}')
            logger.info(f"Payload that will be applied : {json.dumps(payload, indent=2)}")

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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def update_ticket_status(self, ticket_id, detail_id, payload, interfaces=None):
        try:
            logger.info(f"Updating ticket status for ticket id: {ticket_id}")

            if interfaces:
                payload["Interfaces"] = interfaces

            logger.info(f"Payload that will be applied (parsed to PascalCase): {json.dumps(payload)}")

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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_inventory_attributes(self, filters):
        try:
            logger.info(f'Getting inventory_attributes for client ID: {filters["client_id"]}')
            parsed_filters = humps.pascalize(filters)
            logger.info(f"Filters that will be applied (parsed to PascalCase): {json.dumps(parsed_filters)}")
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                    params=parsed_filters,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_outage_ticket(self, client_id, service_number, ticket_contact, interfaces):
        try:
            logger.info(f"Posting outage ticket for client with ID {client_id} and for service number {service_number}")

            if not isinstance(service_number, list):
                service_number = [service_number]

            payload = {
                "ClientID": client_id,
                "WTNs": service_number,
                "RequestDescription": "MetTel's IPA -- Service Outage Trouble",
            }
            if ticket_contact:
                payload["ticketContact"] = ticket_contact

            if interfaces:
                payload["WtnInterfaces"] = {service_number[0]: interfaces}

            logger.info(f"Posting payload {json.dumps(payload)} to create new outage ticket...")

            return_response = dict.fromkeys(["body", "status"])
            url = f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'

            try:
                response = await self._session.post(url, json=payload, headers=self._get_request_headers(), ssl=False)
            except aiohttp.ClientConnectionError as err:
                logger.error(f"A connection error happened while trying to connect to Bruin API. Cause: {err}")
                return_response["body"] = f"Connection error in Bruin API. Cause: {err}"
                return_response["status"] = 500
                return return_response

            status_code = response.status
            if status_code in range(200, 300):
                response_json = await response.json()
                logger.info(f"Got HTTP {status_code} from Bruin when posting outage ticket with payload "
                            f"{json.dumps(payload)}. Response body: {response_json}")
                # The root key may differ depending on the status code...
                ticket_data = response_json.get("assets", response_json.get("items"))[0]

                # HTTP 409 means the service number is already under an in-progress ticket
                # HTTP 471 means the service number is already under a resolved ticket
                # These two codes are embedded in the body of a HTTP 200 response
                if ticket_data["errorCode"] == 409:
                    logger.info(
                        f"Got HTTP 409 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with In-Progress status"
                    )
                    status_code = 409
                elif ticket_data["errorCode"] == 471:
                    logger.info(
                        f"Got HTTP 471 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status"
                    )
                    status_code = 471
                elif ticket_data["errorCode"] == 472:
                    logger.info(
                        f"Got HTTP 472 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status. "
                        f"The existing ticket has been unresolved and it's now In-Progress."
                    )
                    status_code = 472
                elif ticket_data["errorCode"] == 473:
                    logger.info(
                        f"Got HTTP 473 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                        f"There's no need to create a new ticket as there is an existing one with Resolved status for "
                        f"the same location of the service number. The existing ticket has been unresolved and it's "
                        f"now In-Progress, and a new ticket detail has been added for the specified service number."
                    )
                    status_code = 473

                return_response["body"] = ticket_data
                return_response["status"] = status_code

            if status_code == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = status_code
                logger.error(
                    f"Got HTTP 400 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    f"Reason: {response_json}"
                )

            if status_code == 401:
                logger.info("Got HTTP 401 from Bruin.")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if status_code == 403:
                return_response[
                    "body"
                ] = f"Permissions to create a new outage ticket with payload {json.dumps(payload)} were not granted"
                return_response["status"] = status_code
                logger.error(
                    "Got HTTP 403 from Bruin. Bruin client doesn't have permissions to post a new outage ticket with "
                    f"payload {json.dumps(payload)}"
                )

            if status_code == 404:
                logger.error(f"Got HTTP 404 from Bruin when posting outage ticket. Payload: {json.dumps(payload)}")
                return_response["body"] = f"Check mistypings in URL: {url}"
                return_response["status"] = status_code

            if status_code in range(500, 514):
                logger.error(
                    f"Got HTTP {status_code} from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                )
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_outage_ticket_full_response(self, client_id, service_number, ticket_contact, interfaces):
        try:
            logger.info(f"Posting outage ticket full response for client with ID {client_id}, "
                        f"service number {service_number}")

            if not isinstance(service_number, list):
                service_number = [service_number]

            payload = {
                "ClientID": client_id,
                "WTNs": service_number,
                "RequestDescription": "MetTel's IPA -- Service Outage Trouble",
            }
            if ticket_contact:
                payload["ticketContact"] = ticket_contact

            if interfaces:
                payload["WtnInterfaces"] = {service_number[0]: interfaces}

            logger.info(f"Posting payload {json.dumps(payload)} to create new outage ticket...")

            return_response = dict.fromkeys(["body", "status"])
            url = f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'

            try:
                response = await self._session.post(url, json=payload, headers=self._get_request_headers(), ssl=False)
            except aiohttp.ClientConnectionError as err:
                logger.error(f"A connection error happened while trying to connect to Bruin API. Cause: {err}")
                return_response["body"] = f"Connection error in Bruin API. Cause: {err}"
                return_response["status"] = 500
                return return_response

            status_code = response.status
            if status_code in range(200, 300):
                response_json = await response.json()
                logger.info(f"Got HTTP {status_code} from Bruin when posting outage ticket with payload "
                            f"{json.dumps(payload)}. Response body: {response_json}")

                return_response["body"] = response_json
                return_response["status"] = status_code

            if status_code == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = status_code
                logger.error(
                    f"Got HTTP 400 from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                    f"Reason: {response_json}"
                )

            if status_code == 401:
                logger.info("Got HTTP 401 from Bruin.")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if status_code == 403:
                return_response[
                    "body"
                ] = f"Permissions to create a new outage ticket with payload {json.dumps(payload)} were not granted"
                return_response["status"] = status_code
                logger.error(
                    "Got HTTP 403 from Bruin. Bruin client doesn't have permissions to post a new outage ticket with "
                    f"payload {json.dumps(payload)}"
                )

            if status_code == 404:
                logger.error(f"Got HTTP 404 from Bruin when posting outage ticket. Payload: {json.dumps(payload)}")
                return_response["body"] = f"Check mistypings in URL: {url}"
                return_response["status"] = status_code

            if status_code in range(500, 514):
                logger.error(
                    f"Got HTTP {status_code} from Bruin when posting outage ticket with payload {json.dumps(payload)}. "
                )
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_client_info(self, filters):
        try:
            logger.info(f"Getting Bruin client ID for filters: {filters}")
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
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_client_info_by_did(self, did):
        try:
            logger.info(f"Getting Bruin client info by DID: {did}")
            return_response = dict.fromkeys(["body", "status"])

            params = {
                "phoneNumber": did,
                "phoneNumberType": "DID",
            }

            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                    params=params,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def change_detail_work_queue(self, ticket_id, filters):
        try:
            logger.info(f"Changing work queue for ticket detail: {filters} and ticket id : {ticket_id}")
            response = await self._session.put(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                json=filters,
                headers=self._get_request_headers(),
                ssl=False,
            )
            return_response = dict.fromkeys(["body", "status"])

            if response.status in range(200, 299):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.info(f"Work queue changed for ticket detail: {filters}")

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_possible_detail_next_result(self, ticket_id, filters):
        try:
            logger.info(f"Getting work queues for ticket detail: {filters}")
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
                logger.info(f"Got possible next work queue results for : {filters}")

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_ticket_task_history(self, filters):
        try:
            logger.info(f"Getting ticket task history for ticket: {filters}")
            return_response = dict.fromkeys(["body", "status"])
            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filters["ticket_id"]}',
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.info(f"Got ticket task history for : {filters}")

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def unpause_ticket(self, ticket_id, filters):
        try:
            logger.info(f"Unpause ticket for ticket id: {ticket_id} with filters {filters}")
            return_response = dict.fromkeys(["body", "status"])
            try:
                response = await self._session.post(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/detail/unpause',
                    json=filters,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                logger.info(f"Correct unpause ticket for ticket id: {ticket_id} with filters {filters}")
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.info(f"Unpause ticket for ticket id: {ticket_id}")

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_email_tag(self, email_id: str, tag_id: str):
        try:
            logger.info(f"Sending request to /api/Email/{email_id}/tag/{tag_id}")

            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Email/{email_id}/tag/{tag_id}',
                headers=self._get_request_headers(),
                ssl=False,
            )

            logger.info(f"Got response from Bruin. Status: {response.status} Response: {response}.")

            return_response = dict.fromkeys(["body", "status"])

            if response.status == 204:
                return_response["body"] = ""
                return_response["status"] = response.status
            elif response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for email_id {email_id} with tag_id {tag_id}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status == 409:
                logger.error(f"Got 409 from Bruin, resource not posted for email_id {email_id} with tag_id {tag_id}")
                return_response["body"] = f"Tag with ID {tag_id} already present in e-mail with ID {email_id}"
                return_response["status"] = 409

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            logger.error(f"Exception during call to post_email_tag. Error: {e}.")
            return {"body": e.args[0], "status": 500}

    async def get_circuit_id(self, params):
        try:
            parsed_params = humps.pascalize(params)

            logger.info(f"Getting the circuit id from bruin with params {parsed_params}")
            return_response = dict.fromkeys(["body", "status"])
            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                    params=parsed_params,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300) and response.status != 204:
                logger.info(f"Got circuit id from bruin with params: {parsed_params}")
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 204:
                logger.error("Got status 204 from Bruin")
                return_response["body"] = "204 No Content"
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error 400 from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def change_ticket_severity(self, ticket_id, payload):
        return_response = dict.fromkeys(["body", "status"])

        logger.info(f"Changing severity of ticket {ticket_id} using payload {payload}...")
        try:
            response = await self._session.put(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/severity',
                json=payload,
                headers=self._get_request_headers(),
                ssl=False,
            )
        except aiohttp.ClientConnectionError as e:
            logger.error(f"A connection error happened while trying to connect to Bruin API -> {e}")
            return_response["body"] = f"Connection error in Bruin API: {e}"
            return_response["status"] = 500
            return return_response

        if response.status in range(200, 300):
            logger.info(f"Severity of ticket {ticket_id} changed successfully! Payload used was {payload}")
            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = response.status

        if response.status == 400:
            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = response.status
            logger.error(f"Got HTTP 400 from Bruin -> {response_json}")

        if response.status == 401:
            logger.error(f"Got HTTP 401 from Bruin. Re-logging in...")
            await self.login()
            return_response["body"] = BRUIN_401_RESPONSE
            return_response["status"] = response.status

        if response.status == 403:
            logger.error(f"Got HTTP 403 from Bruin")
            return_response["body"] = f"Permissions to change the severity level of ticket {ticket_id} were not granted"
            return_response["status"] = response.status

        if response.status == 404:
            logger.error(f"Got HTTP 404 from Bruin")
            return_response["body"] = BRUIN_404_RESPONSE
            return_response["status"] = response.status

        if response.status in range(500, 513):
            logger.error(f"Got HTTP {response.status} from Bruin")
            return_response["body"] = BRUIN_500_RESPONSE
            return_response["status"] = 500

        return return_response

    async def get_site(self, params):
        try:
            parsed_params = humps.pascalize(params)

            logger.info(f"Getting Bruin Site for params: {params}")
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Site',
                    params=parsed_params,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                logger.info(f"Got HTTP 200 from GET /api/Site for params {json.dumps(params)}")
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                logger.error(f"Got HTTP 403 from Bruin")
                return_response["body"] = {"error": "403 error"}
                return_response["status"] = response.status

            if response.status == 404:
                logger.error(f"Got HTTP 404 from Bruin")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status} from Bruin")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_ticket_contacts(self, params):
        try:
            parsed_params = humps.pascalize(params)

            logger.info(f"Getting Bruin Ticket Contacts for params: {params}")
            logger.info(self._config.BRUIN_CONFIG["base_url"])
            logger.info(parsed_params)
            return_response = dict.fromkeys(["body", "status"])

            try:
                await self.login()
                response = await self._session.get(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/Contacts',
                    params=parsed_params,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                logger.info(f"Got HTTP 200 from GET /api/Ticket/Contacts for params {json.dumps(params)}")
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 400:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                logger.error(f"Got HTTP 403 from Bruin")
                return_response["body"] = {"error": "403 error"}
                return_response["status"] = response.status

            if response.status == 404:
                logger.error(f"Got HTTP 404 from Bruin")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status} from Bruin")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def mark_email_as_done(self, email_id: int):
        try:
            logger.info(f"Marking email as done: {email_id}")
            return_response = dict.fromkeys(["body", "status"])
            payload = {
                "emailId": email_id,
                "status": "Done",
                "resolution": f"Mark as done by {self._config.IPA_SYSTEM_USERNAME_IN_BRUIN}",
                "updatedBy": self._config.IPA_SYSTEM_USERNAME_IN_BRUIN,
            }

            try:
                response = await self._session.post(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Email/status',
                    json=payload,
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error("Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status} from Bruin")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def link_ticket_to_email(self, ticket_id: int, email_id: int):
        try:
            logger.info(f"Linking ticket {ticket_id} with email {email_id}")
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = await self._session.post(
                    f'{self._config.BRUIN_CONFIG["base_url"]}/api/Email/{email_id}/link/ticket/{ticket_id}',
                    headers=self._get_request_headers(),
                    ssl=False,
                )
            except aiohttp.ClientConnectionError as e:
                logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
                return_response["body"] = f"Connection error in Bruin API. {e}"
                return_response["status"] = 500
                return return_response

            if response.status in range(200, 300):
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status

            if response.status == 401:
                logger.error("Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status in range(500, 513):
                logger.error(f"Got HTTP {response.status} from Bruin")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def post_notification_email_milestone(self, payload):
        try:
            logger.info(
                f'Sending milestone email for ticket id {payload["ticket_id"]}, service number'
                f' {payload["detail"]["service_number"]} and notification type'
                f' {payload["notification_type"]}'
            )
            payload = humps.pascalize(payload)
            logger.info(f"Payload that will be applied : {json.dumps(payload, indent=2)}")

            response = await self._session.post(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Notification/email/milestone',
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_asset_topics(self, params: Dict[str, str]) -> BruinResponse:
        logger.info(f"Getting asset topics for: {params}")
        request = BruinGetRequest(path="/api/Ticket/topics", params=params)
        response = await self._bruin_session.get(request)

        if response.status == HTTPStatus.UNAUTHORIZED:
            logger.error(f"Got 401 from Bruin. Re-logging in...")
            await self.login()

        return response

    async def get_ticket_detail_ids_by_ticket_detail_interfaces(self, ticket_id, detail_id, interfaces):
        try:
            logger.info(f"Getting ticket details ids for ticket id: {ticket_id}, "
                        f"detail id: {detail_id}, interfaces: {interfaces}")

            url = (
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/'
                f'details/{detail_id}/detailids?interfaces={",".join(interfaces)}'
            )

            headers = self._get_request_headers()
            headers["api-version"] = "2.0"

            response = await self._session.get(
                url=url,
                headers=headers,
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for for ticket id: {ticket_id}, "
                             f"detail id: {detail_id}, interfaces: {interfaces}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def close_ticket(self, ticket_id, payload):
        try:
            logger.info(f"Closing ticket id: {ticket_id}")

            logger.info(f"Payload that will be applied (parsed to PascalCase): {json.dumps(payload)}")

            response = await self._session.put(
                f'{self._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/close',
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
                logger.error(f"Got error from Bruin {response_json}")

            if response.status == 401:
                logger.error(f"Got 401 from Bruin. Re-logging in...")
                await self.login()
                return_response["body"] = BRUIN_401_RESPONSE
                return_response["status"] = response.status

            if response.status == 403:
                response_json = await response.json()
                return_response["body"] = response_json
                return_response["status"] = response.status
                logger.error(f"Forbidden error from Bruin {response_json}")

            if response.status == 404:
                logger.error(f"Got 404 from Bruin, resource not posted for payload of {payload}")
                return_response["body"] = BRUIN_404_RESPONSE
                return_response["status"] = 404

            if response.status in range(500, 513):
                logger.error(f"Got {response.status}.")
                return_response["body"] = BRUIN_500_RESPONSE
                return_response["status"] = 500

            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}
