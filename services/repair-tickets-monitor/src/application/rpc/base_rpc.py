import logging
from http import HTTPStatus
from typing import Any, Optional

from dataclasses import dataclass
from framework.nats.client import Client as NatsClient
from pydantic import BaseModel, Field
from shortuuid import uuid

log = logging.getLogger(__name__)


@dataclass
class Rpc:
    """
    Component that acts as an nats client wrapper.
    """

    _nats_client: NatsClient
    _topic: str
    _timeout: int

    async def send(self, rpc_request: "RpcRequest") -> "RpcResponse":
        """
        Send the request message and return a parsed response.
        Responses other than OK will raise an RpcFailedError.
        Any other raised error will be wrapped into an RpcError.
        :raise RpcFailedError: any response that is not OK
        :raise RpcError: if the request fails by any other means.
        :param rpc_request: the request being sent
        :return: a parsed response
        """
        log.debug(f"send(rpc_request={rpc_request})")

        payload = rpc_request.bytes()
        try:
            response = await self._nats_client.request(subject=self._topic, payload=payload, timeout=self._timeout)
            rpc_response = RpcResponse.parse_raw(response.data)
        except Exception as error:
            raise RpcError from error

        if rpc_response.is_ok():
            log.debug(f"_nats_client.rpc_request(subject={self._topic}, payload={payload}) [OK]")
        else:
            raise RpcFailedError(request=rpc_request, response=rpc_response)

        log.debug(f"send() [OK]")
        return rpc_response


class RpcRequest(BaseModel):
    """
    Data structure that represents a base request.
    """

    request_id: str = Field(default_factory=uuid)
    body: Any = None

    def bytes(self) -> bytes:
        return self.json(separators=(",", ":")).encode()


class RpcResponse(BaseModel):
    """
    Data structure that represents an rpc response.
    """

    status: int
    body: Any = None

    def is_ok(self) -> bool:
        return self.status == HTTPStatus.OK


class RpcError(Exception):
    pass


@dataclass
class RpcFailedError(RpcError):
    request: RpcRequest
    response: RpcResponse
    message: Optional[str] = None

    def __str__(self):
        return self.__repr__()
