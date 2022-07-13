import logging
from dataclasses import dataclass
from http import HTTPStatus
from logging import Logger, LoggerAdapter
from typing import Any, Optional

from framework.nats.client import Client as NatsClient
from pydantic import BaseModel
from shortuuid import uuid

log = logging.getLogger(__name__)


@dataclass
class Rpc:
    """
    Component that acts as an nats client wrapper.
    """

    _nats_client: NatsClient
    _logger: Logger
    _topic: str
    _timeout: int

    def start(self) -> (str, "RpcLogger"):
        """
        Start the rpc by generating a request_id and an appropriate _logger.
        :return: a request_id and a _logger
        """
        request_id = uuid()
        return RpcRequest(request_id=request_id), RpcLogger(request_id=request_id, logger=self._logger)

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
        logger = RpcLogger(request_id=rpc_request.request_id, logger=self._logger)
        logger.debug(f"send(rpc_request={rpc_request})")

        try:
            response = await self._nats_client.request(
                subject=self._topic, payload=rpc_request.bytes(), timeout=self._timeout
            )
            rpc_response = RpcResponse.parse_raw(response.data)
        except Exception as error:
            raise RpcError from error

        if rpc_response.is_ok():
            logger.debug(f"_nats_client.rpc_request(subject={self._topic}, payload={rpc_request.json()}) [OK]")
        else:
            raise RpcFailedError(request=rpc_request, response=rpc_response)

        logger.debug(f"send() [OK]")
        return rpc_response


class RpcRequest(BaseModel):
    """
    Data structure that represents a base request.
    """

    request_id: str
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


class RpcLogger(LoggerAdapter):
    """
    Logger that provides request contextual data.
    """

    def __init__(self, logger: Logger, request_id: str):
        super().__init__(logger=logger, extra={"request_id": request_id})

    def process(self, base_rpc, kwargs):
        extra_str = ", ".join(f"{key}={value}" for key, value in self.extra.items())
        return "[%s] %s" % (extra_str, base_rpc), kwargs


class RpcError(Exception):
    pass


@dataclass
class RpcFailedError(RpcError):
    request: RpcRequest
    response: RpcResponse
    message: Optional[str] = None

    def __str__(self):
        return self.__repr__()
