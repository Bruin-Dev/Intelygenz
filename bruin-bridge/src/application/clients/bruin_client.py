import base64

import requests


class BruinClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger
        self._bearer_token = ""

    def login(self):
        self._logger.info("Logging into Bruin...")
        creds = str.encode(self._config["client_id"] + ":" + self._config["client_secret"])
        headers = {
            "authorization": f"Basic {base64.b64encode(creds).decode()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form_data = {
            "grant_type": "client_credentials",
            "scope": "public_api"
        }

        try:
            response = requests.post(f'{self._config["login_url"]}/identity/connect/token',
                                     data=form_data,
                                     headers=headers)
            self._bearer_token = response.json()["access_token"]
            self._logger.info("Logged into Bruin!")

        except Exception as err:
            self._logger.error("An error occurred while trying to login to Bruin")
            self._logger.error(f"{err}")

    def get_request_headers(self):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        headers = {
            "authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json-patch+json"
        }
        return headers

    def get_ticket_detail(self, ticket_id):
        self._logger.info(f'Getting ticket details for ticket id: {ticket_id}')
        response = requests.get(f'{self._config["base_url"]}/api/Ticket/{ticket_id}/details',
                                headers=self._get_request_headers(),
                                verify=False)
        # Put the parse of response object in repository
        return response.json()["ticketDetails"]

    def post_ticket_note(self, ticket_id, ticket_note):
        self._logger.info(f'Getting posting notes for ticket id: {ticket_id}')
        payload = {
            "note": ticket_note
        }
        response = requests.post(f'{self._config["base_url"]}/api/Ticket/{ticket_id}/notes',
                                 headers=self._get_request_headers(),
                                 json=payload,
                                 verify=False)
        return response.json()
