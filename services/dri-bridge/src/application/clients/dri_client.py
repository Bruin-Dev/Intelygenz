import json

import aiohttp


class DRIClient:
    def __init__(self, config, logger):
        self._config = config
        self._logger = logger

        self._bearer_token = ""
        self._session = aiohttp.ClientSession(trace_configs=config.AIOHTTP_CONFIG["tracers"])

    async def login(self):
        self._logger.info("Logging into DRI...")
        login_credentials = {
            "email": self._config.DRI_CONFIG["email_acc"],
            "password": self._config.DRI_CONFIG["email_password"],
        }
        try:
            response = await self._session.post(
                f"{self._config.DRI_CONFIG['base_url']}/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=login_credentials,
                allow_redirects=False,
            )

            self._bearer_token = (await response.json())["authorization_token"]
            self._logger.info("Logged into DRI!")
        except Exception as err:
            self._logger.error("An error occurred while trying to login to DRI")
            self._logger.error(f"Error: {err}")

    def _get_request_headers(self):
        if not self._bearer_token:
            raise Exception("Missing BEARER token")

        headers = {
            "authorization": f"Bearer {self._bearer_token}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }
        return headers

    async def get_task_id(self, serial_number, parameter_set):
        json_parameter_set = json.dumps(parameter_set)
        self._logger.info(f"Getting task id from serial {serial_number} with parameters {json_parameter_set}...")
        try:
            response = await self._session.get(
                f"{self._config.DRI_CONFIG['base_url']}/acs/device/{serial_number}/parameter_returnid?data="
                f"{json_parameter_set}",
                headers=self._get_request_headers(),
                allow_redirects=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status == 401:
                self._logger.error(f"Got 401 from DRI. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from DRI"
                return_response["status"] = response.status
                return return_response

            if response.status == 504:
                self._logger.error(f"Got {response.status}. Getting task_id of {serial_number} timed out")
                return_response["body"] = f"Getting task_id of {serial_number} timed out"
                return_response["status"] = response.status
                return return_response

            response_json = await response.json()

            return_response["body"] = response_json
            return_response["status"] = 200

            if response.status not in range(200, 300):
                self._logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = response.status
                return return_response

            return return_response

        except Exception as err:
            self._logger.error(f"An error occurred while trying to get the task id from serial {serial_number}")
            self._logger.error(f"Error: {err}")
            return {"body": err.args[0], "status": 500}

    async def get_task_results(self, serial_number, task_id):
        self._logger.info(f"Checking if {task_id} for serial {serial_number} is complete...")
        try:
            response = await self._session.get(
                f"{self._config.DRI_CONFIG['base_url']}/acs/device/{serial_number}/parameter_tid?transactionid="
                f"{task_id}",
                headers=self._get_request_headers(),
                allow_redirects=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status == 401:
                self._logger.error(f"Got 401 from DRI. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from DRI"
                return_response["status"] = response.status
                return return_response

            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = 200

            if response.status not in range(200, 300):
                self._logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = response.status
                return return_response

            return return_response
        except Exception as err:
            self._logger.error(f"An error occurred while checking if {task_id} for serial {serial_number} is complete")
            self._logger.error(f"Error: {err}")
            return {"body": err.args[0], "status": 500}

    async def get_pending_task_ids(self, serial_number):
        self._logger.info(f"Getting list of pending task ids for serial number {serial_number}...")
        try:
            response = await self._session.get(
                f"{self._config.DRI_CONFIG['base_url']}/acs/device/{serial_number}/taskpending",
                headers=self._get_request_headers(),
                allow_redirects=False,
            )

            return_response = dict.fromkeys(["body", "status"])

            if response.status == 401:
                self._logger.error(f"Got 401 from DRI. Re-logging in...")
                await self.login()
                return_response["body"] = "Got 401 from DRI"
                return_response["status"] = response.status
                return return_response

            response_json = await response.json()
            return_response["body"] = response_json
            return_response["status"] = 200

            if response.status not in range(200, 300):
                self._logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = response.status
                return return_response

            return return_response
        except Exception as err:
            self._logger.error(
                f"An error occurred while getting list of pending task ids for serial number {serial_number}"
            )
            self._logger.error(f"Error: {err}")
            return {"body": err.args[0], "status": 500}
