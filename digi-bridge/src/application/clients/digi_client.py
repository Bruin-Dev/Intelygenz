import base64
import json

import aiohttp
import humps


class DiGiClient:

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger
        self._bearer_token = ""
        self._session = aiohttp.ClientSession()

    async def login(self):
        self._logger.info("Logging into DiGi...")
        login_credentials = f'{self._config.DIGI_CONFIG["client_id"]}:{self._config.DIGI_CONFIG["client_secret"]}'
        login_credentials = login_credentials.encode()
        login_credentials_b64 = base64.b64encode(login_credentials).decode()

        headers = {
            "authorization": f"Basic {login_credentials_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        form_data = {
            "grant_type": "client_credentials",
            "scope": "write:dms"
        }

        try:
            response = await self._session.post(
                f'{self._config.DIGI_CONFIG["base_url"]}/Identity/rest/oauth/token',
                data=form_data,
                headers=headers,
            )

            self._bearer_token = (await response.json())["access_token"]
            self._logger.info("Logged into DiGi!")
        except Exception as err:
            self._logger.error("An error occurred while trying to login to DiGi")
            self._logger.error(f"Error: {err}")

    def _get_request_headers(self, params):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        token = {
            "authorization": f"Bearer {self._bearer_token}",
        }
        headers = {**token, **params}
        return headers

    async def reboot(self, params):
        try:
            parsed_params = humps.pascalize(params)

            self._logger.info(f'Rebooting DiGi device with params {json.dumps(parsed_params)}')

            response = await self._session.get(
                f"{self._config.DIGI_CONFIG['base_url']}/DeviceManagement_API/rest/Recovery/RecoverDevice",
                params=parsed_params,
                headers=self._get_request_headers(),
                ssl=False,
            )
            return_response = dict.fromkeys(["body", "status"])

            response_json = await response.json()
            response_error = response_json.get('error')
            response_message = response_json.get('message')
            return_response["body"] = response_json

            if response.status not in range(200, 300):
                self._logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = 500
            if response_error is not None:
                self._logger.error(f"Got an error of {response_error}")
                return_response["status"] = 400
            if response_message.contains('Aborted'):
                self._logger.error(f"DiGi reboot aborted with message returning: {response_message}")
                return_response["status"] = 400

            return return_response

        except Exception as e:
            return {
                'body': e.args[0],
                'status': 500
            }
