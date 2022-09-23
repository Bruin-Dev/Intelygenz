import json
import logging
from dataclasses import dataclass, field
from string import Template
from typing import Any, Dict, Generic, Optional, Protocol, Type, TypeVar

import aiohttp
from pydantic import BaseModel

R = TypeVar("R")
JSON_SEPARATORS = (",", ":")

log = logging.getLogger(__name__)


@dataclass
class HttpRequest:
    path: str
    method: str
    query_params: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    data: Any = None

    def json(self) -> Optional[str]:
        if self.data is None:
            return None
        elif isinstance(self.data, BaseModel):
            return self.data.json(separators=JSON_SEPARATORS)
        else:
            return json.dumps(self.data, separators=JSON_SEPARATORS)


@dataclass
class HttpResponse(Generic[R]):
    status: int
    data: Optional[R] = None


@dataclass
class BeforeRequestHook(Protocol):
    async def __call__(
        self,
        http_client: "HttpClient",
        http_request: HttpRequest,
        response_type: Optional[Type[R]] = None,
        **kwargs,
    ):
        pass


@dataclass
class HttpClient:
    session: aiohttp.ClientSession

    async def send(
        self,
        http_request: HttpRequest,
        response_type: Optional[Type[R]] = None,
        before_request_hook: Optional[BeforeRequestHook] = None,
        **kwargs,
    ) -> HttpResponse[R]:
        log.debug(f"send(request={http_request}, kwargs={kwargs})")

        if before_request_hook:
            await before_request_hook(
                http_client=self,
                http_request=http_request,
                response_type=response_type,
                **kwargs,
            )

        response = await self.session.request(
            method=http_request.method,
            url=Template(http_request.path).substitute(http_request.path_params),
            json=http_request.json(),
            headers=http_request.headers,
            **kwargs,
        )

        response_body = await response.text()

        http_response = HttpResponse(response.status)
        if not response_body:
            return http_response

        # Parse the response
        if not response_type or response_type == Any:
            try:
                http_response.data = json.loads(response_body)
            except Exception as e:
                raise ValueError(f"Response body can't be deserialized to JSON: {response_body}") from e
        elif issubclass(response_type, BaseModel):
            try:
                http_response.data = response_type.parse_raw(response_body)
            except Exception as e:
                raise ValueError(f"Response body can't be deserialized to {response_type}: {response_body}") from e
        else:
            try:
                http_response.data = response_type(response_body)
            except Exception as e:
                raise ValueError(f"Response body can't be deserialized to {response_type}: {response_body}") from e

        return http_response

    async def close(self):
        await self.session.close()
