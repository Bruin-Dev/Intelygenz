import asyncio
import logging

from framework.http.server import Config, Server
from hypercorn.asyncio import serve

log = logging.getLogger(__name__)


class HealthServer(Server):
    def __init__(self, config: Config):
        super().__init__(config)
        self._shutdown_signal = asyncio.Event()
        self._shutdown_completed = asyncio.Event()

    async def run(self):
        """
        Runs the Quart server according to the configuration.
        """
        self._hypercorn_config.loglevel = "ERROR"
        coro = serve(self.server, self._hypercorn_config, shutdown_trigger=self._shutdown_signal.wait)
        task = asyncio.create_task(coro)
        task.add_done_callback(lambda _: self._shutdown_completed.set())

    async def close(self):
        self._shutdown_signal.set()
        await self._shutdown_completed.wait()
