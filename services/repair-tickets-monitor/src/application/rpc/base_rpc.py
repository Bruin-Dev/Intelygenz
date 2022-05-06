from logging import Logger, LoggerAdapter
from typing import Any, Dict

from dataclasses import dataclass
from igz.packages.eventbus.eventbus import EventBus
from pydantic import BaseModel
from shortuuid import uuid

OK_STATUS = 200


@dataclass
class Rpc:
    """
    Component that acts as an event_bus wrapper.
    """
    event_bus: EventBus
    logger: Logger
    topic: str
    timeout: int

    def start(self) -> (str, 'RpcLogger'):
        """
        Start the rpc by generating a request_id and an appropriate logger.
        :return: a request_id and a logger
        """
        request_id = uuid()
        return request_id, RpcLogger(request_id=request_id, logger=self.logger)

    async def send(self, request: 'RpcRequest') -> 'RpcResponse':
        """
        Send the request message and return a parsed response.
        :param request:
        :return:
        """
        response = await self.event_bus.rpc_request(self.topic, request.dict(), timeout=self.timeout)
        return RpcResponse.parse_obj(response)


class RpcRequest(BaseModel):
    """
    Data structure that represents a base request.
    """
    request_id: str


class RpcResponse(BaseModel):
    """
    Data structure that represents an rpc response.
    """
    status: int
    body: Dict[str, Any] = None

    def is_ok(self) -> bool:
        return self.status == OK_STATUS


class RpcLogger(LoggerAdapter):
    """
    Logger that provides request contextual data.
    """

    def __init__(self, logger: Logger, request_id: str):
        super().__init__(logger=logger, extra={"request_id": request_id})

    def process(self, msg, kwargs):
        extra_str = ', '.join(f"{key}={value}" for key, value in self.extra.items())
        return "[%s] %s" % (extra_str, msg), kwargs


class RpcError(Exception):
    pass
