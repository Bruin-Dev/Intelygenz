from config import config
from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from application.actions.edge_list_response import ReportEdgeList
from application.actions.edge_status_response import ReportEdgeStatus
from application.actions.edge_events_for_alert import EventEdgesForAlert
from application.repositories.velocloud_repository import VelocloudRepository
from application.clients.velocloud_client import VelocloudClient

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud bridge starting...")
        self._velocloud_client = VelocloudClient(config, self._logger)
        self._velocloud_repository = VelocloudRepository(config, self._logger, self._velocloud_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_list = NATSClient(config, logger=self._logger)
        self._subscriber_stat = NATSClient(config, logger=self._logger)
        self._subscriber_alert = NATSClient(config, logger=self._logger)
        self._subscriber_event_alert = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_list, consumer_name="list")
        self._event_bus.add_consumer(self._subscriber_stat, consumer_name="status")
        self._event_bus.add_consumer(self._subscriber_alert, consumer_name="alert")
        self._event_bus.add_consumer(self._subscriber_event_alert, consumer_name="event_alert")
        self._event_bus.set_producer(self._publisher)

        self._actions_list = ReportEdgeList(config, self._event_bus, self._velocloud_repository, self._logger)
        self._actions_status = ReportEdgeStatus(config, self._event_bus, self._velocloud_repository, self._logger)
        self._edge_events_for_alert = EventEdgesForAlert(self._event_bus, self._velocloud_repository, self._logger)

        self._report_edge_list = ActionWrapper(self._actions_list, "report_edge_list",
                                               is_async=True, logger=self._logger)
        self._report_edge_status = ActionWrapper(self._actions_status, "report_edge_status",
                                                 is_async=True, logger=self._logger)

        self._alert_edge_event = ActionWrapper(self._edge_events_for_alert, "report_edge_event",
                                               is_async=True, logger=self._logger)

        self._server = QuartServer(config)

    async def start(self):
        self._velocloud_repository.connect_to_all_servers()
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="list", topic="edge.list.request",
                                                 action_wrapper=self._report_edge_list,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="status", topic="edge.status.request",
                                                 action_wrapper=self._report_edge_status,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="event_alert", topic="alert.request.event.edge",
                                                 action_wrapper=self._alert_edge_event,
                                                 queue="velocloud_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
