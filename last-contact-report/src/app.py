from config import config
from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.eventbus import EventBus
from application.actions.alert import Alert
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
import asyncio
from igz.packages.server.api import QuartServer
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from shortuuid import uuid


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Last contact report starting...")
        self._scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._server = QuartServer(config)
        self._service_id = uuid()

        self._publisher = NATSClient(config, logger=self._logger)
        self.subscriber_alert = NATSClient(config, logger=self._logger)
        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self.subscriber_alert, consumer_name="sub-alert")
        self._event_bus.set_producer(self._publisher)

        self._alert = Alert(self._event_bus, self._scheduler, self._logger, config.ALERTS_CONFIG, self._service_id)

        self._receive_alert_edges = ActionWrapper(self._alert, "receive_all_edges", is_async=True, logger=self._logger)

    async def _start(self):
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="sub-alert",
                                                 topic=f"alert.response.all.edges.{self._service_id}",
                                                 action_wrapper=self._receive_alert_edges,
                                                 durable_name="last-contact-report",
                                                 queue="last-contact-report",
                                                 ack_wait=480)

        await self._alert.start_alert_job(exec_on_start=False)
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
