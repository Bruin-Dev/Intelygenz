from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.Logger.logger_client import LoggerClient
import asyncio

logger = LoggerClient(config).get_logger()


class EventValidator:
    expected_event = None

    def __init__(self, expected_event):
        self.expected_event = expected_event

    def set_excpected_event(self, expected_event):
        self.expected_event = expected_event

    def check_event_cb(self, event):
        string_event = event.decode("utf-8")
        logger.info(f'Expected message: {self.expected_event}')
        logger.info(f'Received message: {string_event}')
        assert string_event == self.expected_event


class Container:
    consumer = None
    producer = None
    event_bus = None
    validate_action = None
    expected_event = None
    topic = "test.topic"

    async def run(self):
        self.setup()
        await self.start()

    def setup(self):
        self.consumer = NatsStreamingClient(config, "base-nats-test-consumer", logger=logger)
        self.producer = NatsStreamingClient(config, "base-nats-test-producer", logger=logger)

        self.expected_event = "Some event"
        event_validator = EventValidator(self.expected_event)
        self.validate_action = ActionWrapper(event_validator, "check_event_cb")

        self.event_bus = EventBus(logger=logger)
        self.event_bus.set_producer(self.producer)
        self.event_bus.add_consumer(consumer=self.consumer, consumer_name="base-test-consumer")

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.publish_message(self.topic, self.expected_event)

        await self.event_bus.subscribe_consumer(consumer_name="base-test-consumer", topic=self.topic,
                                                action_wrapper=self.validate_action,
                                                start_at='first')


if __name__ == '__main__':
    logger.info("Base nats test starting...")
    loop = asyncio.get_event_loop()
    container = Container()
    loop.run_until_complete(container.run())
