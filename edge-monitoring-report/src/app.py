import asyncio

from application.actions.edge_monitoring import EdgeMonitoring
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from shortuuid import uuid

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.server.api import QuartServer
import os


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Edge monitoring report starting...")
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)
        self._service_id = uuid()

        self._publisher = NatsStreamingClient(config, f'edge-monitoring-report-publisher-', logger=self._logger)
        self.subscriber_edge = NatsStreamingClient(config, f'edge-monitoring-report-edge-', logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self.subscriber_edge, consumer_name="sub-edge")
        self._event_bus.set_producer(self._publisher)

        self._edge_monitoring = EdgeMonitoring(self._event_bus, self._logger, self._scheduler,
                                               self._service_id, config.ALERTS_CONFIG)

        self._process_edge = ActionWrapper(self._edge_monitoring, "receive_edge", is_async=True, logger=self._logger)

    async def _start(self):
        await self._event_bus.connect()

        await self._edge_monitoring.start_edge_monitor_job(exec_on_start=True)

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
