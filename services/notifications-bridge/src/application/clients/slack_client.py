import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Dict

import aiohttp
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from pydantic import BaseModel

COMMON_HEADERS = {
    "Content-Type": "application/json",
}

logger = logging.getLogger(__name__)


class SlackResponse(BaseModel):
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


def slack_headers() -> Dict[str, str]:
    return {**COMMON_HEADERS}


@dataclass
class SlackClient:
    config: Dict
    url: str = None
    session: ClientSession = None

    async def create_session(self):
        self.session: ClientSession = aiohttp.ClientSession()

    def __post_init__(self):
        self.url = self.config["webhook"]

    async def send_to_slack(self, msg) -> SlackResponse:
        headers = slack_headers()
        try:
            client_response = await self.session.post(self.url, headers=headers, json=msg, ssl=False)
            response = await SlackResponse.from_client_response(client_response)

            if not response.ok():
                logger.warning(f"post(send_to_slack) => response={response}")
            else:
                logger.info(response)

            return response

        except aiohttp.ClientConnectionError as e:
            logger.error(f"post(send_to_slack) => ClientConnectionError: {e}")
            return SlackResponse(body=f"ClientConnectionError: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"post(send_to_slack) => UnexpectedError: {e}")
            return SlackResponse(body=f"Unexpected error: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
