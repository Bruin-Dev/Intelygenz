from logging import Logger
from typing import Dict, Any

import aiohttp
import humps
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from dataclasses import dataclass

COMMON_HEADERS = {
    "Content-Type": "application/json-patch+json",
    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
}


@dataclass
class BruinResponse:
    status: int
    body: Any

    @classmethod
    async def from_client_response(cls, client_response: ClientResponse):
        json = await client_response.json()
        return cls(body=json, status=client_response.status)

    def ok(self) -> bool:
        return self.status in range(200, 300)


@dataclass
class BruinSession:
    """
    Manages the Bruin http session.
    """
    session: ClientSession
    base_url: str
    logger: Logger

    def __post_init__(self):
        self.logger.info(f"Started Bruin session")

    async def get(self, path: str, query_params: Dict[str, str], access_token: str) -> BruinResponse:
        self.logger.debug(f"get(path={path}, query_params={query_params}")

        headers = _bruin_headers(access_token=access_token)
        url = f"{self.base_url}{path}"
        params = humps.pascalize(query_params)

        try:
            client_response = await self.session.get(url, params=params, headers=headers, ssl=False)
            response = await BruinResponse.from_client_response(client_response)

            if not response.ok():
                self.logger.warning(f"get(path={path}) => response={response}")

            return response

        except aiohttp.ClientConnectionError as e:
            self.logger.error(f"get(path={path}) => ClientConnectionError: {e}")
            return BruinResponse(body=f"ClientConnectionError: {e}", status=500)

        except Exception as e:
            self.logger.error(f"get(path={path}) => UnexpectedError: {e}")
            return BruinResponse(body=f"Unexpected error: {e}", status=500)


def _bruin_headers(access_token: str) -> Dict[str, str]:
    return {
        "authorization": f"Bearer {access_token}",
        **COMMON_HEADERS
    }
