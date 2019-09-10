import asyncio
from application.actions.edge_monitoring import EdgeMonitoring
from application.clients.statistic_client import StatisticClient
from application.repositories.edge_repository import EdgeRepository
from application.repositories.prometheus_repository import PrometheusRepository
from application.repositories.statistic_repository import StatisticRepository
from application.repositories.status_repository import StatusRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from redis import Redis
from shortuuid import uuid

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud orchestrator starting...")
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)
        self._service_id = uuid()

        self._publisher = NatsStreamingClient(config, f'velocloud-orchestrator-publisher-', logger=self._logger)
        self.subscriber_edges = NatsStreamingClient(config, f'velocloud-orchestrator-edges-list-', logger=self._logger)
        self.subscriber_edge = NatsStreamingClient(config, f'velocloud-orchestrator-edge-', logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self.subscriber_edges, consumer_name="sub-edges-list")
        self._event_bus.add_consumer(self.subscriber_edge, consumer_name="sub-edge")
        self._event_bus.set_producer(self._publisher)

        self._prometheus_repository = PrometheusRepository(config)
        self._stats_client = StatisticClient(config)
        self._stats_repo = StatisticRepository(config, self._stats_client, self._logger)

        self._redis_client = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._edge_repository = EdgeRepository(self._redis_client, self._logger)

        self._status_repository = StatusRepository(self._redis_client, self._logger)
        self._edge_monitoring = EdgeMonitoring(self._event_bus, self._logger, self._prometheus_repository,
                                               self._scheduler, self._edge_repository, self._status_repository,
                                               self._stats_repo, self._service_id, config)

        self._process_edge_list = ActionWrapper(self._edge_monitoring, "receive_edge_list", is_async=True,
                                                logger=self._logger)
        self._process_edge = ActionWrapper(self._edge_monitoring, "receive_edge", is_async=True, logger=self._logger)

    async def _start(self):
        self._edge_monitoring.start_prometheus_metrics_server()
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="sub-edges-list",
                                                 topic=f"edge.list.response.{self._service_id}",
                                                 action_wrapper=self._process_edge_list,
                                                 durable_name="velocloud_orchestrator",
                                                 queue="velocloud_orchestrator",
                                                 ack_wait=480)

        await self._event_bus.subscribe_consumer(consumer_name="sub-edge",
                                                 topic=f"edge.status.response.{self._service_id}",
                                                 action_wrapper=self._process_edge,
                                                 durable_name="velocloud_orchestrator",
                                                 queue="velocloud_orchestrator")

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
