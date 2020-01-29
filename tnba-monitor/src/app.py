import asyncio
from shortuuid import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
import json
from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("TNBA Monitor starting...")
        self._scheduler = AsyncIOScheduler(timezone=timezone(config.TIMEZONE))
        self._server = QuartServer(config)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)

    async def _start(self):
        await self._event_bus.connect()

        test_message = {
            "request_id": uuid(),
            "ticket_id": 4467303
        }
        prediction = await self._event_bus.publish_message("t7.prediction.request", test_message)
        self._logger.info(f'Got prediction from TNBA API: {json.dumps(prediction, indent=2, default= str)}')
        self._scheduler.start()

    async def start_server(self):
        await self._server.run_server()

    async def run(self):
        await self._start()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
