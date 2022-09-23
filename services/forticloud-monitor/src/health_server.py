import logging
from asyncio import AbstractEventLoop
from dataclasses import dataclass, field

from sanic import HTTPResponse, Sanic
from sanic.server import AsyncioServer

log = logging.getLogger(__name__)
logging.getLogger("sanic.root").setLevel(logging.ERROR)


@dataclass
class HealthServer:
    name: str
    port: int
    server: AsyncioServer = field(init=False)
    sanic: Sanic = Sanic("health_server", log_config=dict(version=1, disable_existing_loggers=True))

    @sanic.route("/_health")
    async def _health(self):
        log.info("Got health check request in /_health")
        return HTTPResponse()

    async def start(self, loop: AbstractEventLoop):
        self.server = await self.sanic.create_server(port=self.port, return_asyncio_server=True)
        await self.server.startup()
        loop.create_task(self.server.start_serving())

    async def close(self):
        self.server.close()
        await self.server.wait_closed()
        self.sanic.stop()
