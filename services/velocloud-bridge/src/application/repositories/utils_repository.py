from http import HTTPStatus
from typing import Any

from aiohttp import ClientResponse
from pydantic import BaseModel


class GenericResponse(BaseModel):
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
