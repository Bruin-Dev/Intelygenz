import asyncio

import jinja2
import redis

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer

from application.actions.comparison_report import ComparisonReport
from application.actions.outage_monitoring import OutageMonitor
from application.actions.triage import Triage
from application.repositories.comparison_report_renderer import ComparisonReportRenderer
from application.repositories.edge_redis_repository import EdgeRedisRepository
from application.repositories.outage_repository import OutageRepository
from application.repositories.monitoring_map_repository import MonitoringMapRepository
from application.repositories.triage_report_renderer import TriageReportRenderer
from config import config


class Container:

    def __init__(self):
        # LOGGER
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service Outage Monitor starting in {config.MONITOR_CONFIG["environment"]}...')

        # REDIS
        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # SCHEDULER
        self._scheduler = AsyncIOScheduler(timezone=config.MONITOR_CONFIG['timezone'])

        # HEALTHCHECK ENDPOINT
        self._server = QuartServer(config)

        # MESSAGES STORAGE MANAGER
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        # EVENT BUS
        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.set_producer(self._publisher)

        # REPOSITORIES
        self._quarantine_edge_repository = EdgeRedisRepository(redis_client=self._redis_client,
                                                               keys_prefix='EDGES_QUARANTINE', logger=self._logger)
        self._reporting_edge_repository = EdgeRedisRepository(redis_client=self._redis_client,
                                                              keys_prefix='EDGES_TO_REPORT', logger=self._logger)
        self._monitoring_map_repository = MonitoringMapRepository(config=config, scheduler=self._scheduler,
                                                                  event_bus=self._event_bus, logger=self._logger)

        # JINJA2 TEMPLATE ENVIRONMENTS
        self._triage_report_templates_loader = jinja2.FileSystemLoader(searchpath="src/templates/triage")
        self._triage_report_templates_environment = jinja2.Environment(loader=self._triage_report_templates_loader)

        self._comparison_report_templates_loader = jinja2.FileSystemLoader(searchpath="src/templates/comparison_report")
        self._comparison_report_templates_environment = jinja2.Environment(
            loader=self._comparison_report_templates_loader
        )

        # EMAIL TEMPLATE
        self._comparison_report_renderer = ComparisonReportRenderer(
            config, self._comparison_report_templates_environment
        )
        self._triage_report_renderer = TriageReportRenderer(config, self._triage_report_templates_environment)

        # OUTAGE UTILS
        self._outage_repository = OutageRepository(self._logger)

        # ACTIONS
        self._comparison_report = ComparisonReport(self._event_bus, self._logger, self._scheduler,
                                                   self._quarantine_edge_repository,
                                                   self._reporting_edge_repository,
                                                   config, self._comparison_report_renderer,
                                                   self._outage_repository)
        self._outage_monitor = OutageMonitor(self._event_bus, self._logger, self._scheduler,
                                             config, self._outage_repository)
        self._triage = Triage(self._event_bus, self._logger, self._scheduler,
                              config, self._triage_report_renderer, self._outage_repository,
                              self._monitoring_map_repository)

    async def _start(self):
        await self._event_bus.connect()

        await self._comparison_report.report_persisted_edges()
        await self._comparison_report.load_persisted_quarantine()

        # await self._comparison_report.start_service_outage_detector_job(exec_on_start=True)
        # await self._comparison_report.start_service_outage_reporter_job(exec_on_start=False)

        await self._outage_monitor.start_service_outage_monitoring(exec_on_start=True)

        # await self._triage.start_triage_job(exec_on_start=True)

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
