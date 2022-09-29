import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any

import aiohttp

from forticloud_client.assemblers.device_status_response_assembler import device_status_response_assembler
from forticloud_client.exceptions.login_error import LoginError

logger = logging.getLogger(__name__)


@dataclass
class ForticloudClient:
    config: Any
    access_token: str = ""
    expiration_date_token = datetime.utcnow()
    session: aiohttp.ClientSession = None

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        await self.session.close()

    def get_request_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def get_if_need_to_do_login(self):
        need_to_do_login = False

        if not self.access_token:
            need_to_do_login = True
        elif self.expiration_date_token < datetime.utcnow():
            need_to_do_login = True

        return need_to_do_login

    @staticmethod
    def get_expiration_date_for_token(second_to_expires):
        return datetime.utcnow() + timedelta(seconds=second_to_expires)

    async def login(self):
        try:
            await self.create_session()

            response = await self.session.request(
                method="POST",
                url=f"{self.config['base_url']}/auth",
                json={
                    "accountId": self.config["account_id"],
                    "userName": self.config["username"],
                    "password": self.config["password"],
                },
            )

            if response.status != HTTPStatus.OK:
                logger.error(f"Failed to get a Forticloud access token. Got response status: {response.status}")
                raise LoginError

            login_response_in_json_format = await response.json()
            self.access_token = login_response_in_json_format["access_token"]
            self.expiration_date_token = self.get_expiration_date_for_token(login_response_in_json_format["expires_in"])

        except Exception as e:
            logger.exception(e)
            raise LoginError
        finally:
            await self.close_session()

    async def get_devices(self, serial_number, response_content_type="application/json", url_api="", network_id=""):
        get_devices_response = {"status": 200, "body": []}
        try:
            await self.create_session()

            if self.get_if_need_to_do_login():
                await self.login()

            get_device_response = await self.session.request(
                method="GET",
                url=f"{self.config['base_url']}/networks/{network_id}{url_api}{serial_number}",
                headers=self.get_request_headers(),
            )
            get_device_response_status = get_device_response.status

            if get_device_response_status != HTTPStatus.OK:
                get_devices_response["status"] = get_device_response_status
                return get_devices_response
            get_devices_response["body"] = await get_device_response.json(content_type=response_content_type)
            return get_devices_response

        except LoginError as e:
            get_devices_response["status"] = HTTPStatus.INTERNAL_SERVER_ERROR
            return get_devices_response
        finally:
            await self.close_session()

    async def device_strategy(self, device, network_id, serial_number=""):
        devices = []
        if device == "access_points":
            devices = await self.get_devices(
                response_content_type="text/plain",
                url_api="/fap/access_points/",
                network_id=network_id,
                serial_number=serial_number,
            )
        elif device == "switches":
            devices = await self.get_devices(
                url_api="/fsw/switch/switches/", network_id=network_id, serial_number=serial_number
            )
        elif device == "networks":
            devices = await self.get_devices(url_api="", serial_number=serial_number)
        return devices

    async def get_response_device(self, device, network_id=""):
        return await self.device_strategy(device, network_id)

    async def get_device_status(self, network_id, device, serial_number):
        device_response = await self.device_strategy(network_id, device, serial_number)
        return device_status_response_assembler(device_response)
