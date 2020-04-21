import base64
import json
import datetime

import humps
import requests
from tenacity import retry, wait_exponential, stop_after_delay, stop_after_attempt, wait_fixed


class LitClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger
        self._bearer_token = ""
        self._last_token_expires = None
        self._base_url = ""

    def login(self):
        @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
        def login():
            self._logger.info("Logging into Lit...")
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            grant_type = 'password'
            form_data = f'grant_type={grant_type}' \
                        f'&client_id={self._config.LIT_CONFIG["client_id"]}' \
                        f'&client_secret={self._config.LIT_CONFIG["client_secret"]}' \
                        f'&username={self._config.LIT_CONFIG["client_username"]}' \
                        f'&password={self._config.LIT_CONFIG["client_password"]}' \
                        f'{self._config.LIT_CONFIG["client_security_token"]}'

            try:
                response = requests.post(f'{self._config.LIT_CONFIG["login_url"]}',
                                         data=form_data,
                                         headers=headers)
                data = response.json()
                if "access_token" not in data.keys():
                    raise Exception("Not access_token")
                if "instance_url" not in data.keys():
                    raise Exception("Not instance_url")
                self._bearer_token = data["access_token"]
                self._base_url = data["instance_url"]
                self._last_token_expires = datetime.datetime.now()
                self._logger.info("Logged into Lit!")

            except Exception as err:
                self._logger.error("An error occurred while trying to login to Lit")
                self._logger.error(f"{err}")
                raise err
            return True

        try:
            return login()
        except Exception as e:
            return e.args[0]

    def _get_request_headers(self):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        # TODO: check if there is a better way
        if self._last_token_expires < datetime.datetime.now() - datetime.timedelta(minutes=110):
            self._logger.error("Token expired, relogin to Lit")
            self.login()

        headers = {
            "authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

        return headers

    def create_dispatch(self, payload):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def create_dispatch():
            self._logger.info(f'Creating dispatch...')
            self._logger.info(f'Payload that will be applied : {payload}')

            response = requests.post(f'{self._base_url}/services/apexrest/NewDispatch/',
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
                self._logger.error(f"Got error from Lit {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Lit, re-login")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Lit, resource not posted for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Lit"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return create_dispatch()
        except Exception as e:
            return e.args[0]

    def get_dispatch(self, dispatch_number):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def get_dispatch():
            self._logger.info(f'Getting dispatch...')
            self._logger.info(f'Getting the dispatch of dispatch number : {dispatch_number}')

            response = requests.get(f'{self._base_url}/services/apexrest/GetDispatch/{dispatch_number}',
                                    headers=self._get_request_headers(),
                                    verify=False)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Lit {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Lit, re-login")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Lit, resource not got for dispatch number: {dispatch_number}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Lit"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return get_dispatch()
        except Exception as e:
            return e.args[0]

    def update_dispatch(self, payload):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def update_dispatch():
            self._logger.info(f'Updating dispatch...')
            self._logger.info(f'Payload that will be applied : {json.dumps(payload, indent=2)}')

            response = requests.post(f'{self._base_url}/services/apexrest/UpdateDispatch/',
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
                self._logger.error(f"Got error from Lit {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Lit, re-login")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Lit, resource not updated for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Lit"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return update_dispatch()
        except Exception as e:
            return e.args[0]

    def upload_file(self, dispatch_id, payload, file_name, file_content_type="application/octet-stream"):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def upload_file():
            self._logger.info(f'Upload file to dispatch dispatch...')
            self._logger.info(f'Payload that will be applied : {len(payload)}')

            headers = self._get_request_headers()

            # Udpate headers with file_content_type
            headers["Content-Type"] = file_content_type
            # Mandatory field
            headers["filename"] = file_name

            if 'application/pdf' == file_content_type:
                raw_data = base64.b64encode(payload)
            else:
                raw_data = payload.decode()

            response = requests.request("POST",
                                        f'{self._base_url}/services/apexrest/UploadDispatchFile/{dispatch_id}',
                                        headers=headers, data=raw_data, verify=False)

            return_response = dict.fromkeys(["body", "status"])

            if response.status_code in range(200, 300):
                return_response["body"] = response.json()
                return_response["status"] = response.status_code

            if response.status_code == 400:
                return_response["body"] = response.json()
                return_response["status"] = response.status_code
                self._logger.error(f"Got error from Lit {response.json()}")

            if response.status_code == 401:
                self._logger.error(f"Got 401 from Lit, re-login")
                self.login()
                return_response["body"] = "Maximum retries while relogin"
                return_response["status"] = 401
                raise Exception(return_response)

            if response.status_code == 404:
                self._logger.error(f"Got 404 from Lit, resource not updated for payload of {payload}")
                return_response["body"] = "Resource not found"
                return_response["status"] = 404

            if response.status_code in range(500, 513):
                self._logger.error(f"Got {response.status_code}. Retrying...")
                return_response["body"] = "Got internal error from Lit"
                return_response["status"] = 500
                raise Exception(return_response)

            return return_response

        try:
            return upload_file()
        except Exception as e:
            return e.args[0]
