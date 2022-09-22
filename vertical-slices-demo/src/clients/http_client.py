from dataclasses import dataclass, field
from http import HTTPStatus
from string import Template
from typing import Any, Dict

import aiohttp


@dataclass
class HttpRequest:
    body: Any
    method: str
    path: str
    path_params: Dict[str, str] = field(default_factory=dict)


@dataclass
class HttpResponse:
    status: int
    body: str

    @property
    def is_ok(self):
        return self.status == HTTPStatus.OK


@dataclass
class HttpClient:
    session: aiohttp.ClientSession

    async def send(self, request: HttpRequest):
        template = Template(request.path)
        response = await self.session.request(
            request.method,
            template.substitute(request.path_params),
            json=request.body,
        )

        return HttpResponse(response.status, await response.text())

    async def close(self):
        await self.session.close()
