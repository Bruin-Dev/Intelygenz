import asyncio
import redis
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.storage_managers import RedisStorageManager
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer
from prometheus_client import start_http_server

from application.actions.change_detail_work_queue import ChangeDetailWorkQueue
from application.actions.change_ticket_severity import ChangeTicketSeverity
from application.actions.get_attributes_serial import GetAttributeSerial
from application.actions.get_circuit_id import GetCircuitID
from application.actions.get_client_info import GetClientInfo
from application.actions.get_client_info_by_did import GetClientInfoByDID
from application.actions.get_management_status import GetManagementStatus
from application.actions.get_next_results_for_ticket_detail import GetNextResultsForTicketDetail
from application.actions.get_service_number_topics import GetServiceNumberTopics
from application.actions.get_single_ticket_basic_info import GetSingleTicketBasicInfo
from application.actions.get_site import GetSite
from application.actions.get_ticket_details import GetTicketDetails
from application.actions.get_ticket_overview import GetTicketOverview
from application.actions.get_ticket_task_history import GetTicketTaskHistory
from application.actions.get_tickets import GetTicket
from application.actions.get_tickets_basic_info import GetTicketsBasicInfo
from application.actions.link_ticket_to_email import LinkTicketToEmail
from application.actions.mark_email_as_done import MarkEmailAsDone
from application.actions.open_ticket import OpenTicket
from application.actions.post_email_tag import PostEmailTag
from application.actions.post_multiple_notes import PostMultipleNotes
from application.actions.post_note import PostNote
from application.actions.post_notification_email_milestone import PostNotificationEmailMilestone
from application.actions.post_outage_ticket import PostOutageTicket
from application.actions.post_ticket import PostTicket
from application.actions.resolve_ticket import ResolveTicket
from application.actions.unpause_ticket import UnpauseTicket
from application.clients.bruin_client import BruinClient
from application.repositories.bruin_repository import BruinRepository
from application.repositories.endpoints_usage_repository import EndpointsUsageRepository
from config import config


class Container:

    def __init__(self):
        self._logger = LoggerClient(config).get_logger()
        self._logger.info("Bruin bridge starting...")

        self._redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        self._redis_client.ping()

        # Prepare tracers to be used when making HTTP requests
        self._endpoints_usage_repository = EndpointsUsageRepository()
        config.generate_aio_tracers(
            endpoints_usage_repository=self._endpoints_usage_repository,
        )

        self._bruin_client = BruinClient(self._logger, config)
        self._bruin_repository = BruinRepository(self._logger, config, self._bruin_client)

        self._message_storage_manager = RedisStorageManager(self._logger, self._redis_client)

        self._publisher = NATSClient(config, logger=self._logger)

        self._subscriber_tickets = NATSClient(config, logger=self._logger)
        self._subscriber_tickets_basic_info = NATSClient(config, logger=self._logger)
        self._subscriber_single_ticket_basic_info = NATSClient(config, logger=self._logger)
        self._subscriber_ticket_overview = NATSClient(config, logger=self._logger)
        self._subscriber_details = NATSClient(config, logger=self._logger)
        self._subscriber_affecting_details_by_edge_serial = NATSClient(config, logger=self._logger)
        self._subscriber_outage_details_by_edge_serial = NATSClient(config, logger=self._logger)
        self._subscriber_post_note = NATSClient(config, logger=self._logger)
        self._subscriber_post_multiple_notes = NATSClient(config, logger=self._logger)
        self._subscriber_post_ticket = NATSClient(config, logger=self._logger)
        self._subscriber_open_ticket = NATSClient(config, logger=self._logger)
        self._subscriber_resolve_ticket = NATSClient(config, logger=self._logger)
        self._subscriber_get_attributes_serial = NATSClient(config, logger=self._logger)
        self._subscriber_get_management_status = NATSClient(config, logger=self._logger)
        self._subscriber_post_outage_ticket = NATSClient(config, logger=self._logger)
        self._subscriber_get_client_info = NATSClient(config, logger=self._logger)
        self._subscriber_get_client_info_by_did = NATSClient(config, logger=self._logger)
        self._subscriber_change_work_queue = NATSClient(config, logger=self._logger)
        self._subscriber_get_ticket_task_history = NATSClient(config, logger=self._logger)
        self._subscriber_get_next_results_for_ticket_detail = NATSClient(config, logger=self._logger)
        self._subscriber_unpause_ticket = NATSClient(config, logger=self._logger)
        self._subscriber_get_circuit_id = NATSClient(config, logger=self._logger)
        self._subscriber_post_email_tag = NATSClient(config, logger=self._logger)
        self._subscriber_change_ticket_severity = NATSClient(config, logger=self._logger)
        self._subscriber_get_site = NATSClient(config, logger=self._logger)
        self._subscriber_mark_email_as_done = NATSClient(config, logger=self._logger)
        self._subscriber_link_ticket_to_email = NATSClient(config, logger=self._logger)
        self._subscriber_post_notification_email_milestone = NATSClient(config, self._logger)
        self._subscriber_get_service_number_topics = NATSClient(config, self._logger)

        self._event_bus = EventBus(self._message_storage_manager, logger=self._logger)
        self._event_bus.add_consumer(self._subscriber_tickets, consumer_name="tickets")
        self._event_bus.add_consumer(self._subscriber_tickets_basic_info, consumer_name="tickets_basic_info")
        self._event_bus.add_consumer(self._subscriber_single_ticket_basic_info,
                                     consumer_name="single_ticket_basic_info")
        self._event_bus.add_consumer(self._subscriber_ticket_overview, consumer_name="ticket_overview")
        self._event_bus.add_consumer(self._subscriber_details, consumer_name="ticket_details")
        self._event_bus.add_consumer(
            self._subscriber_affecting_details_by_edge_serial,
            consumer_name="affecting_ticket_details_by_edge_serial"
        )
        self._event_bus.add_consumer(
            self._subscriber_outage_details_by_edge_serial,
            consumer_name="outage_ticket_details_by_edge_serial"
        )
        self._event_bus.add_consumer(self._subscriber_post_note, consumer_name="post_note")
        self._event_bus.add_consumer(self._subscriber_post_multiple_notes, consumer_name="post_multiple_notes")
        self._event_bus.add_consumer(self._subscriber_post_ticket, consumer_name="post_ticket")
        self._event_bus.add_consumer(self._subscriber_open_ticket, consumer_name="open_ticket")
        self._event_bus.add_consumer(self._subscriber_resolve_ticket, consumer_name="resolve_ticket")
        self._event_bus.add_consumer(self._subscriber_get_attributes_serial, consumer_name="get_attributes_serial")
        self._event_bus.add_consumer(self._subscriber_get_management_status, consumer_name="get_management_status")
        self._event_bus.add_consumer(self._subscriber_post_outage_ticket, consumer_name="post_outage_ticket")
        self._event_bus.add_consumer(self._subscriber_get_client_info, consumer_name="get_client_info")
        self._event_bus.add_consumer(self._subscriber_get_client_info_by_did, consumer_name="get_client_info_by_did")
        self._event_bus.add_consumer(self._subscriber_change_work_queue, consumer_name="change_work_queue")
        self._event_bus.add_consumer(self._subscriber_get_ticket_task_history, consumer_name="get_ticket_task_history")
        self._event_bus.add_consumer(
            self._subscriber_get_next_results_for_ticket_detail,
            consumer_name="get_next_results_for_ticket_detail",
        )
        self._event_bus.add_consumer(self._subscriber_unpause_ticket, consumer_name="unpause_ticket")
        self._event_bus.add_consumer(self._subscriber_post_email_tag, consumer_name="post_email_tag")
        self._event_bus.add_consumer(self._subscriber_get_circuit_id, consumer_name="get_circuit_id")
        self._event_bus.add_consumer(self._subscriber_change_ticket_severity, consumer_name="change_ticket_severity")
        self._event_bus.add_consumer(self._subscriber_get_site, consumer_name="get_site")
        self._event_bus.add_consumer(self._subscriber_mark_email_as_done, consumer_name="mark_email_as_done")
        self._event_bus.add_consumer(self._subscriber_link_ticket_to_email, consumer_name="link_ticket_to_email")
        self._event_bus.add_consumer(
            self._subscriber_post_notification_email_milestone,
            consumer_name='post_notification_email_milestone'
        )
        self._event_bus.add_consumer(
            self._subscriber_get_service_number_topics,
            consumer_name='get_service_number_topics'
        )

        self._event_bus.set_producer(self._publisher)

        self._get_tickets = GetTicket(self._logger, config.BRUIN_CONFIG, self._event_bus,
                                      self._bruin_repository)
        self._get_tickets_basic_info = GetTicketsBasicInfo(self._logger, self._event_bus, self._bruin_repository)
        self._get_single_ticket_basic_info = GetSingleTicketBasicInfo(self._logger, self._event_bus,
                                                                      self._bruin_repository)
        self._get_ticket_overview = GetTicketOverview(self._logger, config.BRUIN_CONFIG, self._event_bus,
                                                      self._bruin_repository)
        self._get_ticket_details = GetTicketDetails(self._logger, self._event_bus, self._bruin_repository)
        self._post_note = PostNote(self._logger, self._event_bus, self._bruin_repository)
        self._post_multiple_notes = PostMultipleNotes(self._logger, self._event_bus, self._bruin_repository)
        self._post_ticket = PostTicket(self._logger, self._event_bus, self._bruin_repository)
        self._open_ticket = OpenTicket(self._logger, self._event_bus, self._bruin_repository)
        self._resolve_ticket = ResolveTicket(self._logger, self._event_bus, self._bruin_repository)
        self._get_attributes_serial = GetAttributeSerial(self._logger, self._event_bus, self._bruin_repository)
        self._get_management_status = GetManagementStatus(self._logger, self._event_bus, self._bruin_repository)
        self._post_outage_ticket = PostOutageTicket(self._logger, self._event_bus, self._bruin_repository)
        self._get_client_info = GetClientInfo(self._logger, self._event_bus, self._bruin_repository)
        self._get_client_info_by_did = GetClientInfoByDID(self._logger, self._event_bus, self._bruin_repository)
        self._change_work_queue = ChangeDetailWorkQueue(self._logger, self._event_bus, self._bruin_repository)
        self._get_ticket_task_history = GetTicketTaskHistory(self._logger, self._event_bus, self._bruin_repository)
        self._get_next_results_for_ticket_detail = GetNextResultsForTicketDetail(
            self._logger, self._event_bus, self._bruin_repository
        )
        self._unpause_ticket = UnpauseTicket(self._logger, self._event_bus, self._bruin_repository)
        self._post_email_tag = PostEmailTag(self._logger, self._event_bus, self._bruin_repository)
        self._get_circuit_id = GetCircuitID(self._logger, self._event_bus, self._bruin_repository)
        self._change_ticket_severity = ChangeTicketSeverity(self._logger, self._event_bus, self._bruin_repository)
        self._get_site = GetSite(self._logger, self._event_bus, self._bruin_repository)
        self._mark_email_as_done = MarkEmailAsDone(self._logger, self._event_bus, self._bruin_repository)
        self._link_ticket_to_email = LinkTicketToEmail(self._logger, self._event_bus, self._bruin_repository)
        self._post_notification_email_milestone = PostNotificationEmailMilestone(
            self._logger,
            self._event_bus,
            self._bruin_repository
        )
        self._get_service_number_topics = GetServiceNumberTopics(
            self._logger,
            self._event_bus,
            self._bruin_repository
        )

        self._report_bruin_ticket = ActionWrapper(self._get_tickets, "get_all_tickets",
                                                  is_async=True, logger=self._logger)
        self._action_get_tickets_basic_info = ActionWrapper(self._get_tickets_basic_info, "get_tickets_basic_info",
                                                            is_async=True, logger=self._logger)
        self._action_get_single_ticket_basic_info = ActionWrapper(self._get_single_ticket_basic_info,
                                                                  "get_single_ticket_basic_info",
                                                                  is_async=True, logger=self._logger)
        self._action_get_ticket_detail = ActionWrapper(self._get_ticket_details, "send_ticket_details",
                                                       is_async=True, logger=self._logger)
        self._action_get_ticket_overview = ActionWrapper(self._get_ticket_overview, "get_ticket_overview",
                                                         is_async=True, logger=self._logger)
        self._action_post_note = ActionWrapper(self._post_note, "post_note",
                                               is_async=True, logger=self._logger)
        self._action_post_multiple_notes = ActionWrapper(self._post_multiple_notes, "post_multiple_notes",
                                                         is_async=True, logger=self._logger)
        self._action_post_ticket = ActionWrapper(self._post_ticket, "post_ticket",
                                                 is_async=True, logger=self._logger)
        self._action_open_ticket = ActionWrapper(self._open_ticket, "open_ticket",
                                                 is_async=True, logger=self._logger)
        self._action_resolve_ticket = ActionWrapper(self._resolve_ticket, "resolve_ticket",
                                                    is_async=True, logger=self._logger)
        self._action_get_attributes_serial = ActionWrapper(self._get_attributes_serial, "get_attributes_serial",
                                                           is_async=True, logger=self._logger,
                                                           )
        self._action_get_management_status = ActionWrapper(self._get_management_status, "get_management_status",
                                                           is_async=True, logger=self._logger,
                                                           )
        self._action_post_outage_ticket = ActionWrapper(self._post_outage_ticket, "post_outage_ticket",
                                                        is_async=True, logger=self._logger,
                                                        )
        self._action_get_client_info = ActionWrapper(self._get_client_info, "get_client_info",
                                                     is_async=True, logger=self._logger,
                                                     )
        self._action_get_client_info_by_did = ActionWrapper(self._get_client_info_by_did, "get_client_info_by_did",
                                                            is_async=True, logger=self._logger,
                                                            )
        self._action_change_work_queue = ActionWrapper(self._change_work_queue, "change_detail_work_queue",
                                                       is_async=True, logger=self._logger,
                                                       )
        self._action_get_ticket_task_history = ActionWrapper(self._get_ticket_task_history,
                                                             "get_ticket_task_history",
                                                             is_async=True, logger=self._logger,
                                                             )
        self._action_get_next_results_for_ticket_detail = ActionWrapper(self._get_next_results_for_ticket_detail,
                                                                        "get_next_results_for_ticket_detail",
                                                                        is_async=True, logger=self._logger,
                                                                        )
        self._action_unpause_ticket = ActionWrapper(self._unpause_ticket, "unpause_ticket",
                                                    is_async=True, logger=self._logger)
        self._action_get_circuit_id = ActionWrapper(self._get_circuit_id, "get_circuit_id", is_async=True,
                                                    logger=self._logger)
        self._action_post_email_tag = ActionWrapper(self._post_email_tag, "post_email_tag", is_async=True,
                                                    logger=self._logger)
        self._action_change_ticket_severity = ActionWrapper(self._change_ticket_severity, "change_ticket_severity",
                                                            is_async=True, logger=self._logger)
        self._action_get_site = ActionWrapper(self._get_site, "get_site", is_async=True, logger=self._logger)
        self._action_mark_email_as_done = ActionWrapper(self._mark_email_as_done,
                                                        "mark_email_as_done", is_async=True, logger=self._logger)
        self._action_link_ticket_to_email = ActionWrapper(self._link_ticket_to_email,
                                                          "link_ticket_to_email", is_async=True, logger=self._logger)
        self._action_post_notification_email_milestone = ActionWrapper(
            self._post_notification_email_milestone,
            'post_notification_email_milestone',
            is_async=True,
            logger=self._logger
        )
        self._action_get_service_number_topics = ActionWrapper(
            self._get_service_number_topics,
            'get_service_number_topics',
            is_async=True,
            logger=self._logger
        )

        self._server = QuartServer(config)

    async def start(self):
        self._start_prometheus_metrics_server()

        await self._event_bus.connect()
        await self._bruin_client.login()
        await self._event_bus.subscribe_consumer(consumer_name="tickets", topic="bruin.ticket.request",
                                                 action_wrapper=self._report_bruin_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="tickets_basic_info", topic="bruin.ticket.basic.request",
                                                 action_wrapper=self._action_get_tickets_basic_info,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="single_ticket_basic_info",
                                                 topic="bruin.single_ticket.basic.request",
                                                 action_wrapper=self._action_get_single_ticket_basic_info,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="ticket_details", topic="bruin.ticket.details.request",
                                                 action_wrapper=self._action_get_ticket_detail,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="ticket_overview", topic="bruin.ticket.overview.request",
                                                 action_wrapper=self._action_get_ticket_overview,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_note", topic="bruin.ticket.note.append.request",
                                                 action_wrapper=self._action_post_note,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_multiple_notes",
                                                 topic="bruin.ticket.multiple.notes.append.request",
                                                 action_wrapper=self._action_post_multiple_notes,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_ticket", topic="bruin.ticket.creation.request",
                                                 action_wrapper=self._action_post_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="open_ticket",
                                                 topic="bruin.ticket.status.open",
                                                 action_wrapper=self._action_open_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="resolve_ticket",
                                                 topic="bruin.ticket.status.resolve",
                                                 action_wrapper=self._action_resolve_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_attributes_serial",
                                                 topic="bruin.inventory.attributes.serial",
                                                 action_wrapper=self._action_get_attributes_serial,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_management_status",
                                                 topic="bruin.inventory.management.status",
                                                 action_wrapper=self._action_get_management_status,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_outage_ticket",
                                                 topic="bruin.ticket.creation.outage.request",
                                                 action_wrapper=self._action_post_outage_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_client_info",
                                                 topic="bruin.customer.get.info",
                                                 action_wrapper=self._action_get_client_info,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_client_info_by_did",
                                                 topic="bruin.customer.get.info_by_did",
                                                 action_wrapper=self._action_get_client_info_by_did,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="change_work_queue",
                                                 topic="bruin.ticket.change.work",
                                                 action_wrapper=self._action_change_work_queue,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_ticket_task_history",
                                                 topic="bruin.ticket.get.task.history",
                                                 action_wrapper=self._action_get_ticket_task_history,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_next_results_for_ticket_detail",
                                                 topic="bruin.ticket.detail.get.next.results",
                                                 action_wrapper=self._action_get_next_results_for_ticket_detail,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="unpause_ticket",
                                                 topic="bruin.ticket.unpause",
                                                 action_wrapper=self._action_unpause_ticket,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="post_email_tag", topic="bruin.email.tag.request",
                                                 action_wrapper=self._action_post_email_tag,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_circuit_id",
                                                 topic="bruin.get.circuit.id",
                                                 action_wrapper=self._action_get_circuit_id,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="change_ticket_severity",
                                                 topic="bruin.change.ticket.severity",
                                                 action_wrapper=self._action_change_ticket_severity,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="get_site",
                                                 topic="bruin.get.site",
                                                 action_wrapper=self._action_get_site,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="mark_email_as_done",
                                                 topic="bruin.mark.email.done",
                                                 action_wrapper=self._action_mark_email_as_done,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name="link_ticket_to_email",
                                                 topic="bruin.link.ticket.email",
                                                 action_wrapper=self._action_link_ticket_to_email,
                                                 queue="bruin_bridge")
        await self._event_bus.subscribe_consumer(consumer_name='post_notification_email_milestone',
                                                 topic='bruin.notification.email.milestone',
                                                 action_wrapper=self._action_post_notification_email_milestone,
                                                 queue='bruin_bridge')
        await self._event_bus.subscribe_consumer(consumer_name='get_service_number_topics',
                                                 topic='bruin.get.topics',
                                                 action_wrapper=self._action_get_service_number_topics,
                                                 queue='bruin_bridge')

    async def start_server(self):
        await self._server.run_server()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG['port'])


if __name__ == '__main__':
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start(), loop=loop)
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()
