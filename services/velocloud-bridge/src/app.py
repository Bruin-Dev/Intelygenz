import asyncio

import redis
from application.actions.edge_events_for_alert import EventEdgesForAlert
from application.actions.enterprise_edge_list import EnterpriseEdgeList
from application.actions.enterprise_events_for_alert import EventEnterpriseForAlert
from application.actions.enterprise_name_list_response import EnterpriseNameList
from application.actions.gateway_status_metrics import GatewayStatusMetrics
from application.actions.get_edge_links_series import GetEdgeLinksSeries
from application.actions.links_configuration import LinksConfiguration
from application.actions.links_metric_info import LinksMetricInfo
from application.actions.links_with_edge_info import LinksWithEdgeInfo
from application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList
from application.actions.network_gateway_list import NetworkGatewayList
from application.clients.velocloud_client import VelocloudClient
from application.repositories.velocloud_repository import VelocloudRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import config
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server


class Container:
    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

        self._velocloud_client = VelocloudClient(config, self._logger, self._scheduler)
        self._velocloud_repository = VelocloudRepository(config, self._logger, self._velocloud_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_enterprise_name_list = NATSClient(config, logger=self._logger)
        self._subscriber_links_with_edge_info = NATSClient(config, logger=self._logger)
        self._subscriber_links_metric_info = NATSClient(config, logger=self._logger)
        self._subscriber_enterprise_edge_list = NATSClient(config, logger=self._logger)
        self._subscriber_event_alert = NATSClient(config, logger=self._logger)
        self._subscriber_enterprise_event_alert = NATSClient(config, logger=self._logger)
        self._subscriber_gateway_status_metrics = NATSClient(config, logger=self._logger)
        self._subscriber_links_configuration = NATSClient(config, logger=self._logger)
        self._subscriber_edge_links_series = NATSClient(config, logger=self._logger)
        self._subscriber_network_enterprise_edge_list = NATSClient(config, logger=self._logger)
        self._subscriber_network_gateway_list = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_enterprise_name_list, consumer_name="enterprise_name_list")
        self._event_bus.add_consumer(self._subscriber_links_with_edge_info, consumer_name="links_with_edge_info")
        self._event_bus.add_consumer(self._subscriber_links_metric_info, consumer_name="links_metric_info")
        self._event_bus.add_consumer(self._subscriber_event_alert, consumer_name="event_alert")
        self._event_bus.add_consumer(self._subscriber_enterprise_event_alert, consumer_name="enterprise_event_alert")
        self._event_bus.add_consumer(self._subscriber_enterprise_edge_list, consumer_name="enterprise_edge_list")
        self._event_bus.add_consumer(self._subscriber_links_configuration, consumer_name="links_configuration")
        self._event_bus.add_consumer(self._subscriber_edge_links_series, consumer_name="edge_links_series")
        self._event_bus.add_consumer(
            self._subscriber_network_enterprise_edge_list, consumer_name="network_enterprise_edge_list"
        )
        self._event_bus.add_consumer(self._subscriber_network_gateway_list, consumer_name="network_gateway_list")
        self._event_bus.add_consumer(self._subscriber_gateway_status_metrics, consumer_name="gateway_status_metrics")

        self._event_bus.set_producer(self._publisher)

        self._edge_events_for_alert = EventEdgesForAlert(self._event_bus, self._velocloud_repository, self._logger)
        self._enterprise_events_for_alert = EventEnterpriseForAlert(
            self._event_bus, self._velocloud_repository, self._logger
        )
        self._links_with_edge_info_action = LinksWithEdgeInfo(self._event_bus, self._logger, self._velocloud_repository)
        self._links_metric_info_action = LinksMetricInfo(self._event_bus, self._logger, self._velocloud_repository)
        self._links_configuration_action = LinksConfiguration(self._event_bus, self._velocloud_repository, self._logger)
        self._enterprise_name_list = EnterpriseNameList(self._event_bus, self._velocloud_repository, self._logger)
        self._enterprise_edge_list = EnterpriseEdgeList(self._event_bus, self._velocloud_repository, self._logger)
        self._edge_links_series_action = GetEdgeLinksSeries(self._event_bus, self._velocloud_repository, self._logger)
        self._network_enterprise_edge_list = NetworkEnterpriseEdgeList(
            self._event_bus, self._velocloud_repository, self._logger
        )
        self._network_gateway_list = NetworkGatewayList(self._event_bus, self._velocloud_repository, self._logger)
        self._gateway_status_metrics = GatewayStatusMetrics(self._event_bus, self._velocloud_repository, self._logger)

        self._alert_edge_event = ActionWrapper(
            self._edge_events_for_alert, "report_edge_event", is_async=True, logger=self._logger
        )
        self._alert_enterprise_event = ActionWrapper(
            self._enterprise_events_for_alert, "report_enterprise_event", is_async=True, logger=self._logger
        )
        self._list_enterprise_name = ActionWrapper(
            self._enterprise_name_list, "enterprise_name_list", is_async=True, logger=self._logger
        )

        self._links_with_edge_info = ActionWrapper(
            self._links_with_edge_info_action, "get_links_with_edge_info", is_async=True, logger=self._logger
        )
        self._links_metric_info = ActionWrapper(
            self._links_metric_info_action, "get_links_metric_info", is_async=True, logger=self._logger
        )
        self._list_enterprise_edges = ActionWrapper(
            self._enterprise_edge_list, "enterprise_edge_list", is_async=True, logger=self._logger
        )
        self._links_configuration = ActionWrapper(
            self._links_configuration_action, "links_configuration", is_async=True, logger=self._logger
        )
        self._edge_links_series = ActionWrapper(
            self._edge_links_series_action, "edge_links_series", is_async=True, logger=self._logger
        )
        self._list_network_enterprise_edge = ActionWrapper(
            self._network_enterprise_edge_list, "get_enterprise_edge_list", is_async=True, logger=self._logger
        )
        self._list_network_gateway = ActionWrapper(
            self._network_gateway_list, "get_network_gateway_list", is_async=True, logger=self._logger
        )
        self._get_gateway_status_metrics = ActionWrapper(
            self._gateway_status_metrics, "get_gateway_status_metrics", is_async=True, logger=self._logger
        )

        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._velocloud_repository.connect_to_all_servers()
        await self._event_bus.connect()
        self._scheduler.start()
        await self._event_bus.subscribe_consumer(
            consumer_name="event_alert",
            topic="alert.request.event.edge",
            action_wrapper=self._alert_edge_event,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="enterprise_event_alert",
            topic="alert.request.event.enterprise",
            action_wrapper=self._alert_enterprise_event,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="links_with_edge_info",
            topic="get.links.with.edge.info",
            action_wrapper=self._links_with_edge_info,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="links_metric_info",
            topic="get.links.metric.info",
            action_wrapper=self._links_metric_info,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="enterprise_name_list",
            topic="request.enterprises.names",
            action_wrapper=self._list_enterprise_name,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="enterprise_edge_list",
            topic="request.enterprises.edges",
            action_wrapper=self._list_enterprise_edges,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="links_configuration",
            topic="request.links.configuration",
            action_wrapper=self._links_configuration,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="edge_links_series",
            topic="request.edge.links.series",
            action_wrapper=self._edge_links_series,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="network_enterprise_edge_list",
            topic="request.network.enterprise.edges",
            action_wrapper=self._list_network_enterprise_edge,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="network_gateway_list",
            topic="request.network.gateway.list",
            action_wrapper=self._list_network_gateway,
            queue="velocloud_bridge",
        )
        await self._event_bus.subscribe_consumer(
            consumer_name="gateway_status_metrics",
            topic="request.gateway.status.metrics",
            action_wrapper=self._get_gateway_status_metrics,
            queue="velocloud_bridge",
        )

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run_server()


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
