import asyncio
from application.actions.service_outage_triage import ServiceOutageTriage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from shortuuid import uuid

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service outage triage starting in {config.TRIAGE_CONFIG["environment"]}...')
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)
        self._service_id = uuid()

        self._publisher = NatsStreamingClient(config, f'service-outage-triage-publisher-', logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._service_outage_triage = ServiceOutageTriage(self._event_bus, self._logger, self._scheduler,
                                                          self._service_id, config)

    async def _start(self):
        await self._event_bus.connect()

        await self._service_outage_triage.start_service_outage_triage_job(exec_on_start=True)

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
