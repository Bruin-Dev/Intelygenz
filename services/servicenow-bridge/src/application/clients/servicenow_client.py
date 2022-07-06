import aiohttp


class ServiceNowClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._base_url = self._config.SERVICENOW_CONFIG["base_url"]
        self._client = aiohttp.ClientSession()
        self._access_token = ""

    def _get_request_headers(self):
        return {
            "Authorization": f"Bearer {self._access_token}",
        }

    async def _request(self, **kwargs):
        try:
            response = await self._client.request(**kwargs, headers=self._get_request_headers())

            if response.status == 401:
                await self._get_access_token()
                response = await self._client.request(**kwargs, headers=self._get_request_headers())

            response_body = await response.json()
            return {"status": response.status, "body": response_body}
        except Exception as e:
            self._logger.exception(e)
            return {"status": 500}

    async def _get_access_token(self):
        self._logger.info("Getting ServiceNow access token...")

        try:
            response = await self._client.request(
                method="POST",
                url=f"{self._base_url}/oauth_token.do",
                data={
                    "grant_type": "password",
                    "client_id": self._config.SERVICENOW_CONFIG["client_id"],
                    "client_secret": self._config.SERVICENOW_CONFIG["client_secret"],
                    "username": self._config.SERVICENOW_CONFIG["username"],
                    "password": self._config.SERVICENOW_CONFIG["password"],
                },
            )

            if response.status == 401:
                self._logger.error("Failed to get a ServiceNow access token")
                return

            response_body = await response.json()
            self._access_token = response_body["access_token"]
            self._logger.info("Got ServiceNow access token!")
        except Exception as e:
            self._logger.exception(e)

    async def report_incident(self, payload):
        self._logger.info(f"Reporting incident with payload: {payload}")

        response = await self._request(
            method="POST",
            url=f"{self._base_url}/api/g_mtcm/intelygenz",
            json=payload,
        )

        return response
