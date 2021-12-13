import redis

from config import config
from application.clients.repair_ticket_client import RepairTicketClient
from application.repositories.repair_ticket_repository import RepairTicketRepository
from application.actions.get_email_inference import GetInference
from application.actions.save_outputs import SaveOutputs
from application.actions.save_created_ticket_feedback import SaveCreatedTicketFeedback

from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.eventbus.action import ActionWrapper

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("KRE Repair Tickets bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        self._repair_ticket_client = RepairTicketClient(self._logger, config)
        self._repair_ticket_repository = RepairTicketRepository(self._logger, self._repair_ticket_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_get_email_inference = NATSClient(config, logger=self._logger)
        self._subscriber_save_outputs = NATSClient(config, logger=self._logger)
        self._subscriber_save_created_ticket_feedback = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_get_email_inference, consumer_name="inference")
        self._event_bus.add_consumer(self._subscriber_save_outputs, consumer_name="outputs")
        self._event_bus.add_consumer(
            self._subscriber_save_created_ticket_feedback,
            consumer_name="created_ticket_feedback"
        )

        self._event_bus.set_producer(self._publisher)

        self._get_inference = GetInference(self._logger, config, self._event_bus, self._repair_ticket_repository)
        self._save_outputs = SaveOutputs(self._logger, config, self._event_bus, self._repair_ticket_repository)
        self._save_created_ticket_feedback = SaveCreatedTicketFeedback(
            self._logger,
            config,
            self._event_bus,
            self._repair_ticket_repository
        )

        self._action_get_inference = ActionWrapper(self._get_inference, "get_inference", is_async=True,
                                                   logger=self._logger)
        self._action_save_outputs = ActionWrapper(self._save_outputs, "save_outputs", is_async=True,
                                                  logger=self._logger)
        self._action_save_created_ticket_feedback = ActionWrapper(
            self._save_created_ticket_feedback,
            "save_created_ticket_feedback",
            is_async=True,
            logger=self._logger
        )

        self._server = QuartServer(config)
        self._logger.info("KRE repair tickets bridge started!")

    async def start(self):
        await self._event_bus.connect()

        await self._event_bus.subscribe_consumer(consumer_name="outputs",
                                                 topic="rta.save_outputs.request",
                                                 action_wrapper=self._action_save_outputs,
                                                 queue="rta_kre_bridge")

        await self._event_bus.subscribe_consumer(consumer_name="inference",
                                                 topic="rta.prediction.request",
                                                 action_wrapper=self._action_get_inference,
                                                 queue="rta_kre_bridge")

        await self._event_bus.subscribe_consumer(consumer_name="created_ticket_feedback",
                                                 topic="rta.created_ticket_feedback.request",
                                                 action_wrapper=self._action_save_created_ticket_feedback,
                                                 queue="rta_kre_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
