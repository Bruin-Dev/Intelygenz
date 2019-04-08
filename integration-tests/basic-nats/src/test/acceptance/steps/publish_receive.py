import asyncio
from behave import given, when, then

from config import config
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient


class EventValidator:
    expected_event = None

    def __init__(self, expected_event):
        self.expected_event = expected_event
        self.received_msg = None

    def check_event_cb(self, event):
        self.received_msg = event.decode("utf-8")


@given('an event bus')
def step_impl(context):
    context.topic = "test.topic"

    consumer = NatsStreamingClient(config, "base-nats-test-consumer")
    producer = NatsStreamingClient(config, "base-nats-test-producer")

    context.expected_event = "Some event"
    event_validator = EventValidator(context.expected_event)
    context.validate_action = ActionWrapper(event_validator, "check_event_cb")
    context.event_bus = EventBus()
    context.event_bus.set_producer(producer)
    context.event_bus.add_consumer(consumer=consumer, consumer_name="base-test-consumer")


@when('a message is published')
def step_impl(context):
    loop = asyncio.get_event_loop()

    async def publish_msg():
        await context.event_bus.connect()
        await context.event_bus.publish_message(context.topic, context.expected_event)
    loop.run_until_complete(publish_msg())


@then('will receive the message')
def step_impl(context):
    loop = asyncio.get_event_loop()

    async def receive_msg():
        await context.event_bus.subscribe_consumer(consumer_name="base-test-consumer", topic=context.topic,
                                                   action_wrapper=context.validate_action,
                                                   start_at='first')
    loop.run_until_complete(receive_msg())

    assert context.validate_action.state_instance.received_msg == context.expected_event
