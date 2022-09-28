import logging
from dataclasses import dataclass, field
from http import HTTPStatus

from aiohttp import ClientSession
from pydantic.main import BaseModel

from bruin_client.models import BruinCredentials, BruinRequest, BruinResponse, BruinToken, RefreshTokenError

log = logging.getLogger(__name__)
TOKEN_METHOD = "POST"
TOKEN_PATH = "/identity/connect/value"
TOKEN_FORM_DATA = {"grant_type": "client_credentials", "scope": "public_api"}


@dataclass
class BruinClient:
    """
    Bruin client that takes care of Bruin authentication and decouples Bruin users
    from the underlying http technology.
    """

    base_url: str
    login_url: str
    credentials: BruinCredentials
    token: BruinToken = field(init=False, default_factory=BruinToken)

    def __post_init__(self):
        self.session = ClientSession(base_url=self.base_url)
        self.login_session = ClientSession(base_url=self.login_url)

    async def send(self, bruin_request: BruinRequest) -> BruinResponse:
        """
        Sends a bruin request honoring the method, url, json, headers and query_params passed.
        :param bruin_request: the bruin request object
        :return: a bruin response
        """
        log.debug(f"send(bruin_request={bruin_request})")
        if self.token.is_expired():
            await self.refresh_token()

        response = await self.session.request(
            method=bruin_request.method,
            url=bruin_request.path,
            json=bruin_request.json,
            headers=self.request_headers() | bruin_request.headers,
            params=bruin_request.query_params,
        )
        log.debug(f"request(...) => {response}")

        return BruinResponse(status=response.status, text=await response.text())

    async def refresh_token(self):
        log.debug(f"refresh_token()")
        # Make the value request
        response = await self.login_session.request(
            method=TOKEN_METHOD,
            url=TOKEN_PATH,
            data=TOKEN_FORM_DATA,
            headers=self.token_headers(),
        )
        log.debug(f"request(...) => {response}")

        # Check if the response was OK
        if response.status != HTTPStatus.OK:
            raise RefreshTokenError(f"Failed to get Bruin value. Server returned a {response.status} status")

        # Parse the response
        response_text = await response.text()
        try:
            token_response = TokenResponse.parse_raw(response_text)
            self.token = BruinToken(value=token_response.access_token, expires_in=token_response.expires_in)
        except Exception as e:
            raise RefreshTokenError(f"Failed to parse Bruin response: {response_text}") from e

    async def close(self):
        await self.session.close()
        await self.login_session.close()

    def request_headers(self):
        return {
            "authorization": f"Bearer {self.token.value}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

    def token_headers(self):
        return {
            "authorization": f"Basic {self.credentials.b64encoded()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }


class TokenResponse(BaseModel):
    access_token: str
    expires_in: int
