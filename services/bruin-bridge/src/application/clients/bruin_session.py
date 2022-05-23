from http import HTTPStatus
from logging import Logger
from typing import Dict, Any, Optional

import aiohttp
import humps
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from dataclasses import dataclass
from pydantic import BaseModel

COMMON_HEADERS = {
    "Content-Type": "application/json-patch+json",
    "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
}


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

    async def get(self, request: 'BruinGetRequest') -> 'BruinResponse':
        self.logger.debug(f"get(request={request})")

        url = f"{self.base_url}{request.path}"
        headers = self.bruin_headers()
        params = humps.pascalize(request.params)

        try:
            client_response = await self.session.get(url, headers=headers, params=params, ssl=False)
            response = await BruinResponse.from_client_response(client_response)

            if not response.ok():
                self.logger.warning(f"get(request={request}) => response={response}")

            return response

        except aiohttp.ClientConnectionError as e:
            self.logger.error(f"get(request={request}) => ClientConnectionError: {e}")
            return BruinResponse(body=f"ClientConnectionError: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            self.logger.error(f"get(request={request}) => UnexpectedError: {e}")
            return BruinResponse(body=f"Unexpected error: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    async def post(self, request: 'BruinPostRequest') -> 'BruinResponse':
        self.logger.debug(f"post(request={request}")

        url = f"{self.base_url}{request.path}"
        headers = self.bruin_headers()

        try:
            client_response = await self.session.post(
                url,
                headers=headers,
                json=request.body.dict(by_alias=True),
                ssl=False
            )
            response = await BruinResponse.from_client_response(client_response)

            if not response.ok():
                self.logger.warning(f"post(request={request}) => response={response}")

            return response

        except aiohttp.ClientConnectionError as e:
            self.logger.error(f"post(request={request}) => ClientConnectionError: {e}")
            return BruinResponse(body=f"ClientConnectionError: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            self.logger.error(f"post(request={request}) => UnexpectedError: {e}")
            return BruinResponse(body=f"Unexpected error: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def bruin_headers(self) -> Dict[str, str]:
        return {
            "authorization": f"Bearer {self.access_token}",
            **COMMON_HEADERS
        }


class BruinResponse(BaseModel):
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
        return self.status == HTTPStatus.OK


class BruinRequest(BaseModel):
    path: str


class BruinGetRequest(BruinRequest):
    params: Dict[str, str]


class BruinPostRequest(BruinRequest):
    body: 'BruinPostBody'


class BruinPostBody(BaseModel):
    class Config:
        allow_population_by_field_name = True


BruinPostRequest.update_forward_refs()
