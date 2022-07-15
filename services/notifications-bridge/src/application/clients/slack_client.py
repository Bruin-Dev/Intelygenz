from http import HTTPStatus
from logging import Logger
from typing import Any, Dict

import aiohttp
from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from dataclasses import dataclass
from pydantic import BaseModel

COMMON_HEADERS = {
    "Content-Type": "application/json",
}


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


@dataclass
class SlackClient:
    config: Dict
    logger: Logger
    url: str = None
    session: ClientSession = aiohttp.ClientSession()

    def __post_init__(self):
        self.url = self.config["webhook"]

    async def send_to_slack(self, msg) -> SlackResponse:
        headers = self.slack_headers()
        try:
            client_response = await self.session.post(self.url, headers=headers, json=msg, ssl=False)
            response = await SlackResponse.from_client_response(client_response)

            if not response.ok():
                self.logger.warning(f"post(send_to_slack) => response={response}")
            else:
                self.logger.info(response)

            return response

        except aiohttp.ClientConnectionError as e:
            self.logger.error(f"post(send_to_slack) => ClientConnectionError: {e}")
            return SlackResponse(body=f"ClientConnectionError: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            self.logger.error(f"post(send_to_slack) => UnexpectedError: {e}")
            return SlackResponse(body=f"Unexpected error: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def slack_headers(self) -> Dict[str, str]:
        return {**COMMON_HEADERS}
