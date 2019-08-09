from config import config
from application.clients.bruin_client import BruinClient
from application.repositories.bruin_repository import BruinRepository
from application.actions.bruin_ticket_response import BruinTicketResponse
from application.actions.get_ticket_details import GetTicketDetails
from application.actions.post_note import PostNote
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
        self._bruin_repository = BruinRepository(self._logger, self._bruin_client)
        self._publisher = NatsStreamingClient(config, f'bruin-bridge-publisher-', logger=self._logger)
        self._subscriber_tickets = NatsStreamingClient(config, f'bruin-bridge-subscriber-', logger=self._logger)
        self._subscriber_details = NatsStreamingClient(config, f'bruin-bridge-subscriber-', logger=self._logger)
        self._subscriber_post_note = NatsStreamingClient(config, f'bruin-bridge-subscriber-', logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_tickets, consumer_name="tickets")
        self._event_bus.add_consumer(self._subscriber_details, consumer_name="ticket_details")
        self._event_bus.add_consumer(self._subscriber_post_note, consumer_name="post_note")
        self._event_bus.set_producer(self._publisher)

        self._get_tickets = BruinTicketResponse(self._logger, config.BRUIN_CONFIG, self._event_bus,
                                                self._bruin_repository)
        self._get_ticket_details = GetTicketDetails(self._logger, self._event_bus, self._bruin_repository)
        self._post_note = PostNote(self._logger, self._event_bus, self._bruin_repository)

        self._report_bruin_ticket = ActionWrapper(self._get_tickets, "report_all_bruin_tickets",
                                                  is_async=True, logger=self._logger)
        self._action_get_ticket_detail = ActionWrapper(self._get_ticket_details, "send_ticket_details",
                                                       is_async=True, logger=self._logger)
        self._action_post_note = ActionWrapper(self._post_note, "post_note",
                                               is_async=True, logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        self._bruin_client.login()
        await self._event_bus.subscribe_consumer(consumer_name="tickets", topic="bruin.ticket.request",
                                                 action_wrapper=self._report_bruin_ticket,
                                                 durable_name="bruin_bridge",
                                                 queue="bruin_bridge",
                                                 ack_wait=480)
        await asyncio.sleep(3)

        await self._event_bus.subscribe_consumer(consumer_name="ticket_details", topic="bruin.ticket.details.request",
                                                 action_wrapper=self._action_get_ticket_detail,
                                                 durable_name="bruin_bridge",
                                                 queue="bruin_bridge",
                                                 ack_wait=480)
        await asyncio.sleep(3)

        await self._event_bus.subscribe_consumer(consumer_name="post_note", topic="bruin.ticket.note.append.request",
                                                 action_wrapper=self._action_post_note,
                                                 durable_name="bruin_bridge",
                                                 queue="bruin_bridge",
                                                 ack_wait=480)

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
