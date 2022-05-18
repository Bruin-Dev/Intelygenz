from logging import Logger
from typing import Dict, Any, Optional

import aiohttp
import humps
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from dataclasses import dataclass

COMMON_HEADERS = {
    "Content-Type": "application/json-patch+json",
    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
}

OK_STATUS = 200


@dataclass
class BruinResponse:
    status: int
    body: Any

    @classmethod
    async def from_client_response(cls, client_response: ClientResponse):
        try:
            json = await client_response.json()
            return cls(body=json, status=client_response.status)
        except Exception:
            text = await client_response.text()
            return cls(body=text, status=client_response.status)

    def ok(self) -> bool:
        return self.status == OK_STATUS


@dataclass
class BruinSession:
    """
    Manages the Bruin http session.
    """
    session: ClientSession
    base_url: str
    logger: Logger

    access_token: Optional[str] = None

    def __post_init__(self):
        self.logger.info(f"Started Bruin session")

    async def get(self, path: str, query_params: Dict[str, str]) -> BruinResponse:
        self.logger.debug(f"get(path={path}, query_params={query_params}")

        url = f"{self.base_url}{path}"
        headers = self.bruin_headers()
        params = humps.pascalize(query_params)

        try:
            client_response = await self.session.get(url, headers=headers, params=params, ssl=False)
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

    def bruin_headers(self) -> Dict[str, str]:
        return {
            "authorization": f"Bearer {self.access_token}",
            **COMMON_HEADERS
        }
