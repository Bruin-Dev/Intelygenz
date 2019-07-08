from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from application.actions.edge_list_response import ReportEdgeList
from application.actions.edge_status_response import ReportEdgeStatus
from application.actions.edges_for_alert import EdgesForAlert
from application.repositories.velocloud_repository import VelocloudRepository

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer
from velocloud_client.client.velocloud_client import VelocloudClient


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud bridge starting...")
        self._velocloud_client = VelocloudClient(config, self._logger)
        self._velocloud_repository = VelocloudRepository(config, self._logger, self._velocloud_client)

        self._publisher = NatsStreamingClient(config, f'velocloud-bridge-publisher-', logger=self._logger)
        self._subscriber_list = NatsStreamingClient(config, f'velocloud-bridge-subscriber-', logger=self._logger)
        self._subscriber_stat = NatsStreamingClient(config, f'velocloud-bridge-subscriber-', logger=self._logger)
        self._subscriber_alert = NatsStreamingClient(config, f'velocloud-bridge-subscriber-', logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_list, consumer_name="list")
        self._event_bus.add_consumer(self._subscriber_stat, consumer_name="status")
        self._event_bus.add_consumer(self._subscriber_alert, consumer_name="alert")
        self._event_bus.set_producer(self._publisher)

        self._actions_list = ReportEdgeList(config, self._event_bus, self._velocloud_repository, self._logger)
        self._actions_status = ReportEdgeStatus(config, self._event_bus, self._velocloud_repository, self._logger)
        self._edges_for_alert = EdgesForAlert(self._event_bus, self._velocloud_repository, self._logger)
        self._report_edge_list = ActionWrapper(self._actions_list, "report_edge_list",
                                               is_async=True, logger=self._logger)
        self._report_edge_status = ActionWrapper(self._actions_status, "report_edge_status",
                                                 is_async=True, logger=self._logger)
        self._alert_edge_list = ActionWrapper(self._edges_for_alert, "report_edge_list",
                                              is_async=True, logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        self._velocloud_repository.connect_to_all_servers()
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="list", topic="edge.list.request",
                                                 action_wrapper=self._report_edge_list,
                                                 durable_name="velocloud_bridge",
                                                 queue="velocloud_bridge",
                                                 ack_wait=480)
        await self._event_bus.subscribe_consumer(consumer_name="status", topic="edge.status.request",
                                                 action_wrapper=self._report_edge_status,
                                                 durable_name="velocloud_bridge",
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="alert", topic="alert.request.all.edges",
                                                 action_wrapper=self._alert_edge_list,
                                                 durable_name="velocloud_bridge",
                                                 queue="velocloud_bridge",
                                                 ack_wait=480)

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
