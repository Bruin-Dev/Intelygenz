import asyncio
from application.actions.edge_events_for_alert import EventEdgesForAlert
from application.actions.edge_id_by_serial_response import SearchForIDsBySerial
from application.actions.edge_list_response import ReportEdgeList
from application.actions.edge_status_response import ReportEdgeStatus
from application.actions.enterprise_name_list_response import EnterpriseNameList
from application.clients.ids_by_serial_client import IDsBySerialClient
from application.clients.velocloud_client import VelocloudClient
from application.repositories.ids_by_serial_repository import IDsBySerialRepository
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.edge_dict_repository import EdgeDictRepository
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import redis

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Velocloud bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._scheduler = AsyncIOScheduler(timezone=config.VELOCLOUD_CONFIG['timezone'])

        self._velocloud_client = VelocloudClient(config, self._logger)
        self._velocloud_repository = VelocloudRepository(config, self._logger, self._velocloud_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)
        self._edge_dict_repository = EdgeDictRepository(self._redis_client, self._logger,
                                                        'VELOCLOUD_BRIDGE_IDS_BY_SERIAL')

        self._ids_by_serial_client = IDsBySerialClient(config, self._logger, self._velocloud_client,
                                                       self._edge_dict_repository)
        self._ids_by_serial_repository = IDsBySerialRepository(config, self._logger, self._ids_by_serial_client,
                                                               self._scheduler)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_list = NATSClient(config, logger=self._logger)
        self._subscriber_stat = NATSClient(config, logger=self._logger)
        self._subscriber_alert = NATSClient(config, logger=self._logger)
        self._subscriber_event_alert = NATSClient(config, logger=self._logger)
        self._subscriber_enterprise_name_list = NATSClient(config, logger=self._logger)
        self._subscriber_id_by_serial = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_list, consumer_name="list")
        self._event_bus.add_consumer(self._subscriber_stat, consumer_name="status")
        self._event_bus.add_consumer(self._subscriber_alert, consumer_name="alert")
        self._event_bus.add_consumer(self._subscriber_event_alert, consumer_name="event_alert")
        self._event_bus.add_consumer(self._subscriber_enterprise_name_list, consumer_name="enterprise_name_list")
        self._event_bus.add_consumer(self._subscriber_id_by_serial, consumer_name="id_by_serial")
        self._event_bus.set_producer(self._publisher)

        self._actions_list = ReportEdgeList(config, self._event_bus, self._velocloud_repository, self._logger)
        self._actions_status = ReportEdgeStatus(config, self._event_bus, self._velocloud_repository, self._logger)
        self._edge_events_for_alert = EventEdgesForAlert(self._event_bus, self._velocloud_repository, self._logger)
        self._enterprise_name_list = EnterpriseNameList(self._event_bus, self._velocloud_repository, self._logger)
        self._edge_ids_by_serial = SearchForIDsBySerial(config, self._event_bus, self._logger,
                                                        self._ids_by_serial_repository)

        self._report_edge_list = ActionWrapper(self._actions_list, "report_edge_list",
                                               is_async=True, logger=self._logger)
        self._report_edge_status = ActionWrapper(self._actions_status, "report_edge_status",
                                                 is_async=True, logger=self._logger)
        self._alert_edge_event = ActionWrapper(self._edge_events_for_alert, "report_edge_event",
                                               is_async=True, logger=self._logger)
        self._list_enterprise_name = ActionWrapper(self._enterprise_name_list, "enterprise_name_list",
                                                   is_async=True, logger=self._logger)
        self._search_for_edge_id = ActionWrapper(self._edge_ids_by_serial, "search_for_edge_id",
                                                 is_async=True, logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        self._velocloud_repository.connect_to_all_servers()
        self._ids_by_serial_repository.start_ids_by_serial_storage_job(exec_on_start=True)
        await self._event_bus.connect()
        self._scheduler.start()
        await self._event_bus.subscribe_consumer(consumer_name="list", topic="edge.list.request",
                                                 action_wrapper=self._report_edge_list,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="status", topic="edge.status.request",
                                                 action_wrapper=self._report_edge_status,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="event_alert", topic="alert.request.event.edge",
                                                 action_wrapper=self._alert_edge_event,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="enterprise_name_list",
                                                 topic="request.enterprises.names",
                                                 action_wrapper=self._list_enterprise_name,
                                                 queue="velocloud_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="id_by_serial",
                                                 topic="edge.ids.by.serial",
                                                 action_wrapper=self._search_for_edge_id,
                                                 queue="velocloud_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
