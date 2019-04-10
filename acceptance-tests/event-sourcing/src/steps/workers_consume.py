import asyncio
from behave import given, when, then

from config import config
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NatsStreamingClient


class EventValidator:

    def __init__(self, consumer_name, subscription_type):
        self.received_events = []
        self.subscription_type = subscription_type
        self.consumer_name = consumer_name

    def check_event_cb(self, event):
        print("Consumer: " + self.consumer_name + "; Message: " + event.decode("utf-8"))
        self.received_events.append(event.decode("utf-8"))


async def publish_msg(context, event, topic_name):
    await context.event_bus.publish_message(topic_name, event)
    context.events_sent.append(event)


async def subscribe(context, consumer_name, topic, subscription_type):
    event_validator = EventValidator(consumer_name, subscription_type)
    context.consumers_events.append(event_validator)

    validate_action = ActionWrapper(event_validator, "check_event_cb")

    if subscription_type == 'individual':
        await context.event_bus.subscribe_consumer(consumer_name=consumer_name, topic=topic,
                                                   action_wrapper=validate_action)
    elif subscription_type == 'group':
        await context.event_bus.subscribe_consumer(consumer_name=consumer_name, topic=topic,
                                                   action_wrapper=validate_action,
                                                   durable_name="name",
                                                   queue="queue")


@given('an event bus and the following consumers')
def step_impl(context):
    context.events_sent = []
    context.consumers_events = []
    context.consumers = []
    loop = asyncio.get_event_loop()
    producer = NatsStreamingClient(config, "base-nats-test-producer")

    context.event_bus = EventBus()
    context.event_bus.set_producer(producer)

    for row in context.table:
        consumer = NatsStreamingClient(config, row['consumer_name'])
        context.event_bus.add_consumer(consumer=consumer, consumer_name=row['consumer_name'])
        context.consumers.append(row['consumer_name'])

    async def bus_connect():
        await context.event_bus.connect()
    loop.run_until_complete(bus_connect())


@when('events are published to the topic "{topic_name}"')
def step_impl(context, topic_name):
    loop = asyncio.get_event_loop()

    for row in context.table:
        loop.run_until_complete(publish_msg(context, row['event'], topic_name))


@when('consumers are subscribed this way to the topic "{topic_name}"')
def step_impl(context, topic_name):
    loop = asyncio.get_event_loop()

    for row in context.table:
        loop.run_until_complete(subscribe(context,
                                          consumer_name=row['consumer_name'],
                                          topic=topic_name,
                                          subscription_type=row['subscription_type']))


@when('consumers are subscribed as "{subscription_type}" to the topic "{topic_name}"')
def step_impl(context, subscription_type, topic_name):
    loop = asyncio.get_event_loop()

    for consumer_name in context.consumers:
        loop.run_until_complete(subscribe(context,
                                          consumer_name=consumer_name,
                                          topic=topic_name,
                                          subscription_type=subscription_type))


@then('each individual consumer will receive all events')
def step_impl(context):
    loop = asyncio.get_event_loop()

    async def wait():
        await asyncio.sleep(1, loop=loop)
    loop.run_until_complete(wait())

    for consumer in context.consumers_events:
        if consumer.subscription_type == "individual":
            assert sorted(consumer.received_events) == sorted(context.events_sent)


@then('group consumers will receive all events without repetitions')
def step_impl(context):
    group_events_received = []
    for consumer in context.consumers_events:
        if consumer.subscription_type == "group":
            group_events_received.extend(consumer.received_events)

    assert sorted(group_events_received) == sorted(context.events_sent)


@then('event bus connection is closed')
def step_impl(context):
    loop = asyncio.get_event_loop()

    async def bus_disconnect():
        await context.event_bus.close_connections()
    loop.run_until_complete(bus_disconnect())
