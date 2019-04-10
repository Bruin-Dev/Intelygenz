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


async def publish_msg(context):
    await context.event_bus.publish_message(context.topic, context.expected_event)


async def receive_msg(context):
    await context.event_bus.subscribe_consumer(consumer_name="base-test-consumer", topic=context.topic,
                                               action_wrapper=context.validate_action,
                                               start_at='first')


@given('an event bus')
def step_impl(context):
    loop = asyncio.get_event_loop()
    consumer = NatsStreamingClient(config, "base-nats-test-consumer")
    producer = NatsStreamingClient(config, "base-nats-test-producer")

    context.expected_event = "Some event"
    event_validator = EventValidator(context.expected_event)
    context.validate_action = ActionWrapper(event_validator, "check_event_cb")
    context.event_bus = EventBus()
    context.event_bus.set_producer(producer)
    context.event_bus.add_consumer(consumer=consumer, consumer_name="base-test-consumer")

    async def bus_connect():
        await context.event_bus.connect()
    loop.run_until_complete(bus_connect())


@when('an event is published')
def step_impl(context):
    context.topic = "test.topic"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish_msg(context))


@when('events are published to the following topics')
def step_impl(context):
    for row in context.table:
        context.topic = row['topic']
        context.expected_event = row['event']
        loop = asyncio.get_event_loop()
        loop.run_until_complete(publish_msg(context))


@then('will receive the event')
def step_impl(context):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive_msg(context))

    assert context.validate_action.state_instance.received_msg == context.expected_event


@then('will receive all events')
def step_impl(context):
    loop = asyncio.get_event_loop()
    for row in context.table:
        context.topic = row['topic']
        context.expected_event = row['event']
        loop.run_until_complete(receive_msg(context))

        assert context.validate_action.state_instance.received_msg == context.expected_event
