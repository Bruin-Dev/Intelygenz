from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from prometheus_client import start_http_server, Summary
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.server.api import QuartServer
import asyncio
from ast import literal_eval

MESSAGES_PROCESSED = Summary('nats_processed_messages', 'Messages processed from NATS')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
logger = LoggerClient(config).get_logger()


class DurableAction:

    def __init__(self, eventbus):
        self.event_bus = eventbus

    @MESSAGES_PROCESSED.time()
    async def durable_print_callback(self, msg):
        logger.info('DURABLE GROUP')
        logger.info(msg)
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        for edge in msg_dict['edges']:
            msg4 = {"request_id": msg_dict['request_id'], "edge": edge}
            await self.event_bus.publish_message("edge.status.request", repr(msg4))
            # logger.info(edge)


class FromFirstAction:
    @REQUEST_TIME.time()
    def first_print_callback(self, msg):
        logger.info('SUBSCRIBER FROM FIRST')
        logger.info(msg)


class Container:
    client1 = None
    client2 = None
    client3 = None
    client4 = None
    event_bus = None
    durable_action = None
    from_first_action = None
    server = None

    async def run(self):
        self.setup()
        await self.start()

    def setup(self):
        self.client1 = NatsStreamingClient(config, "base-microservice-client", logger=logger)
        self.client2 = NatsStreamingClient(config, "base-microservice-client", logger=logger)
        self.client3 = NatsStreamingClient(config, "base-microservice-client", logger=logger)

        base_from_first_action = FromFirstAction()

        self.event_bus = EventBus(logger=logger)
        base_durable_action = DurableAction(self.event_bus)

        self.durable_action = ActionWrapper(base_durable_action, "durable_print_callback", is_async=True, logger=logger)
        self.from_first_action = ActionWrapper(base_from_first_action, "first_print_callback", logger=logger)

        self.event_bus.set_producer(self.client1)

        self.event_bus.add_consumer(consumer=self.client2, consumer_name="consumer2")
        self.event_bus.add_consumer(consumer=self.client3, consumer_name="consumer3")

        self.server = QuartServer(config)

    async def start(self):
        await self.event_bus.connect()

        # Start up the server to expose the metrics.
        start_http_server(9100)
        # Generate some requests.
        logger.info('starting metrics loop')

        await self.event_bus.publish_message("edge.list.request", repr({"request_id": "dead",
                                                                        "filter": [{'host': 'metvco02.mettel.net',
                                                                                    'enterprise_ids': []
                                                                                    }]
                                                                        }
                                                                       )
                                             )

        await self.event_bus.subscribe_consumer(consumer_name="consumer2", topic="edge.list.response",
                                                action_wrapper=self.durable_action,
                                                durable_name="base",
                                                queue="base",
                                                start_at='first')

        await self.event_bus.subscribe_consumer(consumer_name="consumer3", topic="edge.status.response",
                                                action_wrapper=self.from_first_action,
                                                durable_name="name",
                                                queue="queue",
                                                start_at='first')

    async def start_server(self):
        await self.server.run_server()


if __name__ == '__main__':
    logger.info("Base microservice starting...")
    container = Container()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(container.run())
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
