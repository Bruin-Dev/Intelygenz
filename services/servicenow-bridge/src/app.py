import asyncio

import redis
from application.actions.report_incident import ReportIncident
from application.clients.servicenow_client import ServiceNowClient
from application.repositories.servicenow_repository import ServiceNowRepository
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
        self._logger.info("ServiceNow bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # Build up singleton dependencies
        self._servicenow_client = ServiceNowClient(self._logger, config)
        self._servicenow_repository = ServiceNowRepository(self._servicenow_client)
        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)
        self._publisher = NATSClient(config, logger=self._logger)

        # Build NATS clients
        self._subscriber_report_incident = NATSClient(config, logger=self._logger)

        # Add NATS clients as event bus consumers
        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_report_incident, consumer_name="report_incident")
        self._event_bus.set_producer(self._publisher)

        # Instance each action
        self._report_incident = ReportIncident(self._logger, self._event_bus, self._servicenow_repository)

        # Wrap the actions
        self._action_report_incident = ActionWrapper(
            self._report_incident, "report_incident", is_async=True, logger=self._logger
        )

        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()
        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(
            consumer_name="report_incident",
            topic="servicenow.incident.report.request",
            action_wrapper=self._action_report_incident,
            queue="servicenow_bridge",
        )

    async def start_server(self):
        await self._server.run_server()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])


if __name__ == "__main__":
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
