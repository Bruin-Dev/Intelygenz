import asyncio
import logging
import sys
from dataclasses import asdict

import redis
from application.actions.change_detail_work_queue import ChangeDetailWorkQueue
from application.actions.change_ticket_severity import ChangeTicketSeverity
from application.actions.get_asset_topics import GetAssetTopics
from application.actions.get_attributes_serial import GetAttributeSerial
from application.actions.get_circuit_id import GetCircuitID
from application.actions.get_client_info import GetClientInfo
from application.actions.get_client_info_by_did import GetClientInfoByDID
from application.actions.get_management_status import GetManagementStatus
from application.actions.get_next_results_for_ticket_detail import GetNextResultsForTicketDetail
from application.actions.get_single_ticket_basic_info import GetSingleTicketBasicInfo
from application.actions.get_site import GetSite
from application.actions.get_ticket_contacts import GetTicketContacts
from application.actions.get_ticket_details import GetTicketDetails
from application.actions.get_ticket_overview import GetTicketOverview
from application.actions.get_ticket_task_history import GetTicketTaskHistory
from application.actions.get_tickets import GetTicket
from application.actions.get_tickets_basic_info import GetTicketsBasicInfo
from application.actions.link_ticket_to_email import LinkTicketToEmail
from application.actions.mark_email_as_done import MarkEmailAsDone
from application.actions.open_ticket import OpenTicket
from application.actions.post_email_reply import PostEmailReply
from application.actions.post_email_status import PostEmailStatus
from application.actions.post_email_tag import PostEmailTag
from application.actions.post_multiple_notes import PostMultipleNotes
from application.actions.post_note import PostNote
from application.actions.post_notification_email_milestone import PostNotificationEmailMilestone
from application.actions.post_outage_ticket import PostOutageTicket
from application.actions.post_ticket import PostTicket
from application.actions.resolve_ticket import ResolveTicket
from application.actions.subscribe_user import SubscribeUser
from application.actions.unpause_ticket import UnpauseTicket
from application.clients.bruin_client import BruinClient
from application.models import subscriptions
from application.repositories.bruin_repository import BruinRepository
from application.repositories.endpoints_usage_repository import EndpointsUsageRepository
from application.services.sentence_formatter import SentenceFormatter
from config import config
from framework.http.server import Config as HealthConfig
from framework.http.server import Server as HealthServer
from framework.logging.formatters import Papertrail as PapertrailFormatter
from framework.logging.formatters import Standard as StandardFormatter
from framework.logging.handlers import Papertrail as PapertrailHandler
from framework.logging.handlers import Stdout as StdoutHandler
from framework.nats.client import Client
from framework.nats.exceptions import NatsException
from framework.nats.models import *
from framework.nats.temp_payload_storage import RedisLegacy as RedisStorage
from prometheus_client import start_http_server

# Standard output logging
base_handler = StdoutHandler()
base_handler.setFormatter(StandardFormatter(environment_name=config.ENVIRONMENT_NAME))

app_logger = logging.getLogger("application")
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(base_handler)

framework_logger = logging.getLogger("framework")
framework_logger.setLevel(logging.DEBUG)
framework_logger.addHandler(base_handler)

# Papertrail logging
if config.LOG_CONFIG["papertrail"]["active"]:
    pt_handler = PapertrailHandler(
        host=config.LOG_CONFIG["papertrail"]["host"],
        port=config.LOG_CONFIG["papertrail"]["port"],
    )
    pt_handler.setFormatter(
        PapertrailFormatter(
            environment_name=config.ENVIRONMENT_NAME,
            papertrail_prefix=config.LOG_CONFIG["papertrail"]["prefix"],
        )
    )
    app_logger.addHandler(pt_handler)
    framework_logger.addHandler(pt_handler)


def bail_out():
    app_logger.critical("Stopping application...")
    sys.exit(1)


class Container:
    def __init__(self):
        app_logger.info("Bruin bridge starting...")

        # Setup health check server
        self._server = HealthServer(HealthConfig(port=config.QUART_CONFIG["port"]))

        # Setup Redis
        redis_client = redis.Redis(host=config.REDIS["host"], port=6379, decode_responses=True)
        redis_client.ping()

        # Setup NATS
        tmp_redis_storage = RedisStorage(storage_client=redis_client)
        self._nats_client = Client(temp_payload_storage=tmp_redis_storage)

        # Setup aiohttp tracers
        endpoints_usage_repository = EndpointsUsageRepository()
        config.generate_aio_tracers(endpoints_usage_repository=endpoints_usage_repository)

        # Setup Bruin utils
        self._bruin_client = BruinClient(config)
        self._bruin_repository = BruinRepository(config, self._bruin_client)

        # Misc
        self._sentence_formatter = SentenceFormatter(_subject=config.IPA_SYSTEM_USERNAME_IN_BRUIN)

    async def _init_nats_conn(self):
        conn = Connection(servers=config.NATS_CONFIG["servers"])

        try:
            await self._nats_client.connect(**asdict(conn))
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def _init_subscriptions(self):
        try:
            # NOTE: Using dataclasses::asdict() throws a pickle error, so we need to use <dataclass>.__dict__ instead
            cb = ChangeDetailWorkQueue(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.ChangeWorkQueueForTicketTask(cb=cb).__dict__)

            cb = ChangeTicketSeverity(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.ChangeTicketSeverity(cb=cb).__dict__)

            cb = GetAssetTopics(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetAvailableTopicsForAsset(cb=cb).__dict__)

            cb = GetAttributeSerial(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetSerialNumberFromInventoryAttributes(cb=cb).__dict__)

            cb = GetCircuitID(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetServiceNumberByCircuitId(cb=cb).__dict__)

            cb = GetClientInfo(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetCustomerInfoByServiceNumber(cb=cb).__dict__)

            cb = GetClientInfoByDID(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetCustomerInfoByDID(cb=cb).__dict__)

            cb = GetManagementStatus(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetManagementStatus(cb=cb).__dict__)

            cb = GetNextResultsForTicketDetail(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetAvailableWorkQueuesForTask(cb=cb).__dict__)

            cb = GetSingleTicketBasicInfo(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetSingleTicketBasic(cb=cb).__dict__)

            cb = GetSite(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetSiteInfo(cb=cb).__dict__)

            cb = GetTicketContacts(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTicketContacts(cb=cb).__dict__)

            cb = GetTicketDetails(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTicketDetails(cb=cb).__dict__)

            cb = GetTicketOverview(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTicketOverview(cb=cb).__dict__)

            cb = GetTicketTaskHistory(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTicketTaskHistory(cb=cb).__dict__)

            cb = GetTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTickets(cb=cb).__dict__)

            cb = GetTicketsBasicInfo(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.GetTicketsBasic(cb=cb).__dict__)

            cb = LinkTicketToEmail(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.LinkBruinEmailToTicket(cb=cb).__dict__)

            cb = MarkEmailAsDone(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.MarkBruinEmailAsDone(cb=cb).__dict__)

            cb = OpenTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.OpenTicketTask(cb=cb).__dict__)

            cb = PostEmailReply(self._bruin_client)
            await self._nats_client.subscribe(**subscriptions.ReplyToAllContactsInBruinEmail(cb=cb).__dict__)

            cb = PostEmailStatus(self._bruin_client, self._sentence_formatter)
            await self._nats_client.subscribe(**subscriptions.UpdateBruinEmailStatus(cb=cb).__dict__)

            cb = PostEmailTag(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.TagEmail(cb=cb).__dict__)

            cb = PostMultipleNotes(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.PostMultipleNotesToTicket(cb=cb).__dict__)

            cb = PostNote(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.PostNoteToTicket(cb=cb).__dict__)

            cb = PostNotificationEmailMilestone(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.SendEmailMilestoneNotification(cb=cb).__dict__)

            cb = PostOutageTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.CreateOutageTicket(cb=cb).__dict__)

            cb = PostTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.CreateTicket(cb=cb).__dict__)

            cb = ResolveTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.ResolveTicketTask(cb=cb).__dict__)

            cb = SubscribeUser(self._bruin_client)
            await self._nats_client.subscribe(**subscriptions.SubscribeUserToTicket(cb=cb).__dict__)

            cb = UnpauseTicket(self._bruin_repository)
            await self._nats_client.subscribe(**subscriptions.UnpauseTicketTask(cb=cb).__dict__)
        except NatsException as e:
            app_logger.exception(e)
            bail_out()

    async def start(self):
        # Prometheus
        self._start_prometheus_metrics_server()

        # Setup VeloCloud HTTP session
        await self._bruin_client.create_session()
        await self._bruin_client.login()

        # Setup NATS
        await self._init_nats_conn()
        await self._init_subscriptions()

    @staticmethod
    def _start_prometheus_metrics_server():
        start_http_server(config.METRICS_SERVER_CONFIG["port"])

    async def start_server(self):
        await self._server.run()


if __name__ == "__main__":
    container = Container()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(container.start())
    loop.run_until_complete(container.start_server())
    loop.run_forever()
