import asyncio
from application.actions.service_affecting_monitor import ServiceAffectingMonitor
from application.actions.production import ProductionAction
from application.actions.development import DevelopmentAction
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient
from igz.packages.notifier_action.notifier_action import NotifierAction
from igz.packages.server.api import QuartServer
from application.repositories.template_management import TemplateRenderer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info(f'Service Affecting Monitor starting in {config.ENV_CONFIG["environment"]}...')
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)

        self._publisher = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.set_producer(self._publisher)
        self._template_renderer = TemplateRenderer(config)

        self.notifier_action = NotifierAction(self._logger, self._event_bus, config,
                                              ProductionAction, DevelopmentAction)
        self._service_affecting_monitor = ServiceAffectingMonitor(self._event_bus, self._logger, self._scheduler,
                                                                  config, self.notifier_action, self._template_renderer)

    async def _start(self):
        await self._event_bus.connect()

        await self._service_affecting_monitor.start_service_affecting_monitor_job(exec_on_start=True)

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
