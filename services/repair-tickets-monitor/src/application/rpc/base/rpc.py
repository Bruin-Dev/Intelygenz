from logging import Logger

from dataclasses import dataclass, asdict
from igz.packages.eventbus.eventbus import EventBus
from shortuuid import uuid

from application.rpc.base.rpc_logger import RpcLogger
from application.rpc.base.rpc_request import RpcRequest
from application.rpc.base.rpc_response import RpcResponse


@dataclass
class Rpc:
    event_bus: EventBus
    topic: str
    timeout: int
    logger: Logger

    def init_request(self):
        request_id = uuid()
        return request_id, RpcLogger(request_id=request_id, logger=self.logger)

    async def send(self, request: RpcRequest):
        response = await self.event_bus.rpc_request(self.topic, asdict(request), timeout=self.timeout)
        return RpcResponse.from_response(response)
