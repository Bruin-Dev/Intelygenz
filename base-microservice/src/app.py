import json
from datetime import datetime

import asyncio
import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from prometheus_client import start_http_server, Summary
from pytz import timezone
from shortuuid import uuid

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.server.api import QuartServer

MESSAGES_PROCESSED = Summary('nats_processed_messages', 'Messages processed from NATS')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
logger = LoggerClient(config).get_logger()


class DurableAction:
    @MESSAGES_PROCESSED.time()
    def durable_print_callback(self, msg):
        logger.info('DURABLE GROUP')
        logger.info(msg)


class FromFirstAction:
    @REQUEST_TIME.time()
    def first_print_callback(self, msg):
        logger.info('SUBSCRIBER FROM FIRST')
        logger.info(msg)


class RPCAction:
    def __init__(self, event_bus):
        self._event_bus = event_bus

    async def rpc_response(self, msg):
        msg_data = json.loads(msg)
        response_msg = {
            "request_id": msg_data["request_id"],
            "some_field_1": "Sending data related to request here",
            "some_field_2": "Sending data related to request here"
        }
        await self._event_bus.publish_message(msg_data["response_topic"], json.dumps(response_msg))


class Container:

    def __init__(self):
        self._my_scheduler = AsyncIOScheduler(timezone=timezone('US/Eastern'))
        self._service_id1 = uuid()
        self._service_id2 = uuid()
        self._service_id3 = uuid()
        self.redis_connection = redis.Redis(host="redis", port=6379, decode_responses=True)
        self.client1 = NatsStreamingClient(config, logger=logger)
        self.client2 = NatsStreamingClient(config, logger=logger)
        self.client3 = NatsStreamingClient(config, logger=logger)
        self.client4 = NatsStreamingClient(config, logger=logger)
        self.client5 = NatsStreamingClient(config, logger=logger)

        base_durable_action = DurableAction()
        base_from_first_action = FromFirstAction()

        self.durable_action = ActionWrapper(base_durable_action, "durable_print_callback", logger=logger)
        self.from_first_action = ActionWrapper(base_from_first_action, "first_print_callback", logger=logger)

        self.event_bus = EventBus(logger=logger)
        rpc_action = RPCAction(event_bus=self.event_bus)
        self.rpc_action = ActionWrapper(rpc_action, "rpc_response", logger=logger, is_async=True)

        self.event_bus.set_producer(self.client1)

        self.event_bus.add_consumer(consumer=self.client2, consumer_name="consumer2")
        self.event_bus.add_consumer(consumer=self.client3, consumer_name="consumer3")
        self.event_bus.add_consumer(consumer=self.client4, consumer_name="consumer4")
        self.event_bus.add_consumer(consumer=self.client5, consumer_name="consumer5")
        self.server = QuartServer(config)

    async def _publish_msgs(self):
        logger.info(f'Publishing messages')
        msg = {
            "data": "Some message"
        }
        await self.event_bus.publish_message(f'topic1.{self._service_id1}', json.dumps(msg))
        await self.event_bus.publish_message(f'topic1.{self._service_id2}', json.dumps(msg))
        await self.event_bus.publish_message(f'topic1.{self._service_id3}', json.dumps(msg))

    async def start_publish_job(self, exec_on_start=False):
        logger.info(f'Starting publish job')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            logger.info(f'It will be executed now')
        self._my_scheduler.add_job(self._publish_msgs, 'interval', seconds=30,
                                   replace_existing=True, next_run_time=next_run_time,
                                   id='_publish_msgs')

    async def _make_rpc_request(self):
        rpc_request_msg = {
            "request_id": uuid(),
            "response_topic": f'rpc.response.{self._service_id1}',
            "some_field_1": "Sending data related to request here",
            "some_field_2": "Sending data related to request here"
        }
        response = await self.event_bus.rpc_request("rpc.request", json.dumps(rpc_request_msg), timeout=10)
        print(f'Got RPC response with value: {json.dumps(response, indent=2)}')

    async def start(self):
        await self.event_bus.connect()
        # Start up the server to expose the metrics.

        start_http_server(9100)
        # Generate some requests.
        logger.info('starting metrics loop')

        await self.event_bus.subscribe_consumer(consumer_name="consumer4", topic=f'topic1.{self._service_id1}',
                                                action_wrapper=self.from_first_action)

        await self.event_bus.subscribe_consumer(consumer_name="consumer3", topic=f'topic1.{self._service_id2}',
                                                action_wrapper=self.durable_action,
                                                queue="queue")

        await self.event_bus.subscribe_consumer(consumer_name="consumer2", topic=f'topic1.{self._service_id3}',
                                                action_wrapper=self.durable_action,
                                                queue="queue")

        # await self.event_bus.subscribe_consumer(consumer_name="consumer5", topic=f'rpc.request',
        #                                         action_wrapper=self.rpc_action,
        #                                         queue="queue")

        await self.start_publish_job(exec_on_start=True)
        self._my_scheduler.start()

        self.redis_connection.hset("foo", "key", datetime.now().isoformat())
        redis_data = self.redis_connection.hgetall("foo")
        logger.info(f'Data retrieved from Redis: {redis_data["key"]}')

        # await self._make_rpc_request()

    async def run(self):
        await self.start()

    async def start_server(self):
        await self.server.run_server()


if __name__ == '__main__':
    logger.info("Base microservice starting...")
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.run(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
