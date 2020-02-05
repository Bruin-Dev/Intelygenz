import asyncio
from application.actions.service_outage_detector import ServiceOutageDetector
from application.repositories.service_outage_report_template_renderer import ServiceOutageReportTemplateRenderer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis import Redis

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from igz.packages.repositories.edge_repository import EdgeRepository
from igz.packages.repositories.outageutils import OutageUtils


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service Outage Monitor starting in {config.MONITOR_CONFIG["environment"]}...')

        # REDIS
        self._redis_client = Redis(host=config.REDIS["host"], port=6379, decode_responses=True)

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.MONITOR_CONFIG['timezone'])

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # REPOSITORIES
        self._quarantine_edge_repository = EdgeRepository(redis_client=self._redis_client,
                                                          keys_prefix='EDGES_QUARANTINE', logger=self._logger)
        self._reporting_edge_repository = EdgeRepository(redis_client=self._redis_client,
                                                         keys_prefix='EDGES_TO_REPORT', logger=self._logger)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # EMAIL TEMPLATE
        self._template_renderer = ServiceOutageReportTemplateRenderer(config)

        # OUTAGE UTILS
        self._outage_utils = OutageUtils(self._logger)

        # ACTIONS
        self._service_outage_detector = ServiceOutageDetector(self._event_bus, self._logger, self._scheduler,
                                                              self._quarantine_edge_repository,
                                                              self._reporting_edge_repository,
                                                              config, self._template_renderer,
                                                              self._outage_utils)

    async def _start(self):
        await self._event_bus.connect()

        # await self._service_outage_detector.report_persisted_edges()
        # await self._service_outage_detector.load_persisted_quarantine()

        # await self._service_outage_detector.start_service_outage_detector_job(exec_on_start=True)
        # await self._service_outage_detector.start_service_outage_reporter_job(exec_on_start=False)
        await self._service_outage_detector.start_service_outage_monitoring(exec_on_start=True)

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
