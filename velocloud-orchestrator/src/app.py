import asyncio
from application.actions.edge_monitoring import EdgeMonitoring
from application.clients.statistic_client import StatisticClient
from application.repositories.edge_repository import EdgeRepository
from application.repositories.prometheus_repository import PrometheusRepository
from application.repositories.statistic_repository import StatisticRepository
from application.repositories.status_repository import StatusRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud orchestrator starting...")
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        self._prometheus_repository = PrometheusRepository(config)
        self._stats_client = StatisticClient(config)
        self._stats_repo = StatisticRepository(config, self._stats_client, self._logger)

        self._edge_repository = EdgeRepository(self._logger)

        self._status_repository = StatusRepository(self._logger)
        self._edge_monitoring = EdgeMonitoring(self._event_bus, self._logger, self._prometheus_repository,
                                               self._scheduler, self._edge_repository, self._status_repository,
                                               self._stats_repo, config)

    async def _start(self):
        self._edge_monitoring.start_prometheus_metrics_server()
        self._prometheus_repository.reset_counter()
        self._prometheus_repository.reset_edges_counter()

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
