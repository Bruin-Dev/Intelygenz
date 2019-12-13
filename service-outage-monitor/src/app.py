import asyncio
from application.actions.service_outage_detector import ServiceOutageDetector
from application.repositories.edge_repository import EdgeRepository
from application.repositories.service_outage_report_template_renderer import ServiceOutageReportTemplateRenderer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis import Redis

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer


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
        self._quarantine_edge_repository = EdgeRepository(logger=self._logger, redis_client=self._redis_client,
                                                          keys_prefix='EDGES_QUARANTINE')
        self._reporting_edge_repository = EdgeRepository(logger=self._logger, redis_client=self._redis_client,
                                                         keys_prefix='EDGES_TO_REPORT')

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # EMAIL TEMPLATE
        self._template_renderer = ServiceOutageReportTemplateRenderer(config)

        # ACTIONS
        self._service_outage_detector = ServiceOutageDetector(self._event_bus, self._logger, self._scheduler,
                                                              self._quarantine_edge_repository,
                                                              self._reporting_edge_repository,
                                                              config, self._template_renderer)

    async def _start(self):
        await self._event_bus.connect()

        await self._service_outage_detector.load_persisted_quarantine()

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
