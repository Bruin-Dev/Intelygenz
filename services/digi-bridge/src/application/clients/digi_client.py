import base64
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from types import ModuleType

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class DiGiClient:
    config: ModuleType
    expiration_date_for_token: datetime = datetime.utcnow()
    bearer_token: str = ""

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    def check_if_token_is_created_and_valid(self):
        valid_token = False
        if not self.bearer_token:
            msg = f"The token is not created yet"
        elif self.expiration_date_for_token < datetime.utcnow():
            msg = f"The token is not valid because it is expired"
        else:
            valid_token = True
            msg = None
        return valid_token, msg

    @staticmethod
    def get_expiration_date_token(seconds_to_expires):
        return datetime.utcnow() + timedelta(seconds=seconds_to_expires)

    def get_request_headers(self, params):
        return {"authorization": f"Bearer {self.bearer_token}", **params}

    def get_auth_header_for_login(self):
        encoded_token = base64.b64encode(
            f'{self.config.DIGI_CONFIG["client_id"]}:{self.config.DIGI_CONFIG["client_secret"]}'.encode()
        ).decode()
        return f"basic {encoded_token}"

    @staticmethod
    def get_list_aborted_messages_from_json(response_json):
        return [message for message in response_json if "Message" in message and "Aborted" in message["Message"]]

    @staticmethod
    def get_list_of_error_messages_from_json(response_json):
        return [message for message in response_json if message.get("error") is not None]

    async def login(self):
        logger.info("Logging into DiGi...")
        try:
            response = await self.session.post(
                f'{self.config.DIGI_CONFIG["base_url"]}/Identity/rest/oauth/token',
                data={"grant_type": "client_credentials", "scope": "write:dms"},
                headers={
                    "authorization": self.get_auth_header_for_login(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                ssl=False,
            )
            login_response_in_json_format = await response.json()
            self.bearer_token = login_response_in_json_format["access_token"]
            self.expiration_date_for_token = self.get_expiration_date_token(login_response_in_json_format["expires_in"])

            logger.info("Logged into DiGi!")
        except Exception as err:
            logger.error("An error occurred while trying to login to DiGi")
            logger.error(f"Error: {err}")

    async def reboot(self, request_filters):
        try:
            logger.info(f"Rebooting DiGi device with params {request_filters}")
            return_response = {"body": None, "status": None}

            is_valid_token, error_token_msg = self.check_if_token_is_created_and_valid()
            if not is_valid_token:
                bad_token_msg = f"{error_token_msg}. Please try in a few seconds"
                logger.error(bad_token_msg)
                return_response["body"] = bad_token_msg
                return_response["status"] = 401
                return return_response

            response = await self.session.post(
                f"{self.config.DIGI_CONFIG['base_url']}/DeviceManagement_API/rest/Recovery/RecoverDevice",
                headers=self.get_request_headers(request_filters),
                ssl=False,
            )
            response_json = await response.json()

            response_error_list = self.get_list_of_error_messages_from_json(response_json)
            response_abort_messages_list = self.get_list_aborted_messages_from_json(response_json)

            if response.status not in range(200, 300):
                logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = 500

            elif response_error_list:
                logger.error(f"Got an error of {response_error_list}")
                return_response["status"] = 400

            elif response_abort_messages_list:
                logger.error(f"DiGi reboot aborted with message returning: {response_abort_messages_list}")
                return_response["status"] = 400
            else:
                return_response["status"] = 200
            return_response["body"] = response_json
            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}

    async def get_digi_recovery_logs(self, request_filters):
        try:
            logger.info(f"Getting DiGi recovery logs with params {request_filters}")
            return_response = {"body": None, "status": None}

            is_valid_token, error_token_msg = self.check_if_token_is_created_and_valid()
            if not is_valid_token:
                bad_token_msg = f"{error_token_msg}. Please try in a few seconds"
                logger.error(bad_token_msg)
                return_response["body"] = bad_token_msg
                return_response["status"] = 401
                return return_response

            response = await self.session.get(
                f"{self.config.DIGI_CONFIG['base_url']}/DeviceManagement_API/rest/Recovery/Logs",
                headers=self.get_request_headers(request_filters),
                ssl=False,
            )
            response_json = await response.json()

            if response.status not in range(200, 300):
                logger.error(f"Got {response.status}. Response returned {response_json}")
                return_response["status"] = 500

            elif "Error" in response_json.keys():
                logger.error(f"Got an error of {return_response['body']}")
                return_response["status"] = 400

            else:
                return_response["status"] = 200

            return_response["body"] = response_json
            return return_response

        except Exception as e:
            return {"body": e.args[0], "status": 500}
