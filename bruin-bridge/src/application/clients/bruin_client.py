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
