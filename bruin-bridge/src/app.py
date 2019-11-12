from config import config
from application.clients.bruin_client import BruinClient
from application.repositories.bruin_repository import BruinRepository
from application.actions.get_tickets import GetTicket
from application.actions.get_ticket_details import GetTicketDetails
from application.actions.get_ticket_details_by_edge_serial import GetTicketDetailsByEdgeSerial
from application.actions.get_outage_ticket_details_by_edge_serial import GetOutageTicketDetailsByEdgeSerial
from application.actions.post_note import PostNote
from igz.packages.nats.clients import NATSClient
from application.actions.post_ticket import PostTicket
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper

from igz.packages.Logger.logger_client import LoggerClient
import asyncio
from igz.packages.server.api import QuartServer


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Bruin bridge starting...")
        self._bruin_client = BruinClient(self._logger, config)
        self._bruin_repository = BruinRepository(self._logger, self._bruin_client)
        self._publisher = NATSClient(config, logger=self._logger)
        self._subscriber_tickets = NATSClient(config, logger=self._logger)
        self._subscriber_details = NATSClient(config, logger=self._logger)
        self._subscriber_details_by_edge_serial = NATSClient(config, logger=self._logger)
        self._subscriber_outage_details_by_edge_serial = NATSClient(config, logger=self._logger)
        self._subscriber_post_note = NATSClient(config, logger=self._logger)
        self._subscriber_post_ticket = NATSClient(config, logger=self._logger)

        self._event_bus = EventBus(logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_tickets, consumer_name="tickets")
        self._event_bus.add_consumer(self._subscriber_details, consumer_name="ticket_details")
        self._event_bus.add_consumer(
            self._subscriber_details_by_edge_serial,
            consumer_name="ticket_details_by_edge_serial"
        )
        self._event_bus.add_consumer(
            self._subscriber_outage_details_by_edge_serial,
            consumer_name="outage_ticket_details_by_edge_serial"
        )
        self._event_bus.add_consumer(self._subscriber_post_note, consumer_name="post_note")
        self._event_bus.add_consumer(self._subscriber_post_ticket, consumer_name="post_ticket")

        self._event_bus.set_producer(self._publisher)

        self._get_tickets = GetTicket(self._logger, config.BRUIN_CONFIG, self._event_bus,
                                      self._bruin_repository)
        self._get_ticket_details = GetTicketDetails(self._logger, self._event_bus, self._bruin_repository)
        self._get_ticket_details_by_edge_serial = GetTicketDetailsByEdgeSerial(
            self._logger, self._event_bus, self._bruin_repository
        )
        self._get_outage_ticket_details_by_edge_serial = GetOutageTicketDetailsByEdgeSerial(
            self._logger, self._event_bus, self._bruin_repository
        )
        self._post_note = PostNote(self._logger, self._event_bus, self._bruin_repository)
        self._post_ticket = PostTicket(self._logger, self._event_bus, self._bruin_repository)

        self._report_bruin_ticket = ActionWrapper(self._get_tickets, "get_all_tickets",
                                                  is_async=True, logger=self._logger)
        self._action_get_ticket_detail = ActionWrapper(self._get_ticket_details, "send_ticket_details",
                                                       is_async=True, logger=self._logger)
        self._action_get_ticket_detail_by_edge_serial = ActionWrapper(
            self._get_ticket_details_by_edge_serial, "send_ticket_details_by_edge_serial",
            is_async=True, logger=self._logger,
        )
        self._action_get_outage_ticket_detail_by_edge_serial = ActionWrapper(
            self._get_outage_ticket_details_by_edge_serial, "send_outage_ticket_details_by_edge_serial",
            is_async=True, logger=self._logger,
        )
        self._action_post_note = ActionWrapper(self._post_note, "post_note",
                                               is_async=True, logger=self._logger)
        self._action_post_ticket = ActionWrapper(self._post_ticket, "post_ticket",
                                                 is_async=True, logger=self._logger)
        self._server = QuartServer(config)

    async def start(self):
        await self._event_bus.connect()
        self._bruin_client.login()
        await self._event_bus.subscribe_consumer(consumer_name="tickets", topic="bruin.ticket.request",
                                                 action_wrapper=self._report_bruin_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="ticket_details", topic="bruin.ticket.details.request",
                                                 action_wrapper=self._action_get_ticket_detail,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="ticket_details_by_edge_serial",
                                                 topic="bruin.ticket.details.by_edge_serial.request",
                                                 action_wrapper=self._action_get_ticket_detail_by_edge_serial,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="outage_ticket_details_by_edge_serial",
                                                 topic="bruin.ticket.outage.details.by_edge_serial.request",
                                                 action_wrapper=self._action_get_outage_ticket_detail_by_edge_serial,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_note", topic="bruin.ticket.note.append.request",
                                                 action_wrapper=self._action_post_note,
                                                 queue="bruin_bridge")

        await self._event_bus.subscribe_consumer(consumer_name="post_ticket", topic="bruin.ticket.creation.request",
                                                 action_wrapper=self._action_post_ticket,
                                                 queue="bruin_bridge")

    async def start_server(self):
        await self._server.run_server()


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
