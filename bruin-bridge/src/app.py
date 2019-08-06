from config import config
from application.clients.bruin_client import BruinClient
from application.actions.bruin_ticket_response import BruinTicketResponse
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Bruin bridge starting...")
        self._bruin_client = BruinClient(self._logger, config.BRUIN_CONFIG)
        self._publisher = NatsStreamingClient(config, f'bruin-bridge-publisher-', logger=self._logger)
        self._subscriber_tickets = NatsStreamingClient(config, f'bruin-bridge-subscriber-', logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_tickets, consumer_name="tickets")
        self._event_bus.set_producer(self._publisher)

        self._get_tickets = BruinTicketResponse(self._logger, config.BRUIN_CONFIG, self._event_bus, self._bruin_client)
        self._report_bruin_ticket = ActionWrapper(self._get_tickets, "report_all_bruin_tickets",
                                                  is_async=True, logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        await self._event_bus.subscribe_consumer(consumer_name="tickets", topic="bruin.ticket.request",
                                                 action_wrapper=self._report_bruin_ticket,
                                                 durable_name="bruin_bridge",
                                                 queue="bruin_bridge",
                                                 ack_wait=480)
        self._bruin_client.login()

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
