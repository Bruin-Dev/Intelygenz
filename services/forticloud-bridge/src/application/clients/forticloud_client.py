import asyncio
import logging

import aiohttp

logger = logging.getLogger(__name__)


class ForticloudClient:
    def __init__(self, config):
        self._config = config
        self._base_url = self._config.FORTICLOUD_CONFIG["base_url"]
        self._access_token = ""

    async def create_session(self):
        self._session = aiohttp.ClientSession()

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self._session.close())

    def _get_request_headers(self):
        return {
            "Authorization": f"Bearer {self._access_token}",
        }

    async def _request(self, **kwargs):
        try:
            response = await self._session.request(**kwargs, headers=self._get_request_headers())

            if response.status == 401:
                await self._get_access_token()
                response = await self._session.request(**kwargs, headers=self._get_request_headers())

            response_body = await response.json()
            return {"status": response.status, "body": response_body}
        except Exception as e:
            logger.exception(e)
            return {"status": 500}

    async def _get_access_token(self):
        logger.info("Getting Forticloud access token...")

        try:
            response = await self._session.request(
                method="POST",
                url=f"{self._base_url}/api/v1/oauth/token/",
                json={
                    "username": self._config.FORTICLOUD_CONFIG["username"],
                    "password": self._config.FORTICLOUD_CONFIG["password"],
                    "client_id": self._config.FORTICLOUD_CONFIG["client_id"],
                    "grant_type": "password",
                },
            )

            if response.status == 401:
                logger.error("Failed to get a Forticloud access token")
                return

            response_body = await response.json()
            self._access_token = response_body["access_token"]
            logger.info("Got Forticloud access token!")
        except Exception as e:
            logger.exception(e)

    async def template_endpoint(self, payload):
        logger.info(f"Doing something with payload: {payload}")

        response = await self._request(
            method="POST",
            url=f"{self._base_url}/api/v1/endpoint",
            json=payload,
        )

        return response
