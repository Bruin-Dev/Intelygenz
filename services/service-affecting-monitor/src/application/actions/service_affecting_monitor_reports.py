import asyncio
from datetime import datetime, timedelta
from typing import Set

from apscheduler.triggers.cron import CronTrigger
from igz.packages.eventbus.eventbus import EventBus
from pytz import timezone


class ServiceAffectingMonitorReports:
    def __init__(
        self,
        event_bus: EventBus,
        logger,
        scheduler,
        config,
        template_repository,
        bruin_repository,
        notifications_repository,
        email_repository,
        customer_cache_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_repository = template_repository
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository
        self._email_repository = email_repository
        self._ISO_8601_FORMAT_UTC = "%Y-%m-%dT%H:%M:%SZ"
        self._customer_cache_repository = customer_cache_repository

    async def start_service_affecting_monitor_reports_job(self, exec_on_start=False):
        self._logger.info(f"Scheduled task: service affecting monitor reports")

        if exec_on_start:
            await self.monitor_reports()

        cron = CronTrigger.from_crontab(
            self._config.MONITOR_REPORT_CONFIG["crontab"], timezone=timezone(self._config.TIMEZONE)
        )
        self._scheduler.add_job(self.monitor_reports, cron, id=f"_monitor_reports", replace_existing=True)

    async def monitor_reports(self):
        monitor_report_init_time = datetime.utcnow()
        start_date_process = self.get_rounded_date(datetime.utcnow())
        host = self._config.VELOCLOUD_HOST
        configuration = self._config.MONITOR_REPORT_CONFIG["recipients_by_host_and_client_id"][host]
        customer_cache_response = await self._customer_cache_repository.get_cache(
            velo_filter=self._config.MONITOR_CONFIG["velo_filter"]
        )
        customer_cache = customer_cache_response["body"]
        if not customer_cache:
            self._logger.error(
                "[service-affecting-monitor-reports] Got an empty customer cache. Process cannot keep going."
            )
            return

        clients_id = configuration.keys()
        cached_names_by_serial = self.get_serial_and_name_for_cached_edges_with_client_id(customer_cache, clients_id)

        trailing_interval = self.get_trailing_interval_for_date(start_date_process)
        start_date_str = self.get_format_to_string_date(trailing_interval["start"])
        end_date_str = self.get_format_to_string_date(trailing_interval["end"])

        affecting_tickets_per_client = {}

        for client_id in clients_id:
            tickets = await self._bruin_repository.get_affecting_ticket_for_report(
                client_id, start_date_str, end_date_str
            )
            if not tickets:
                tickets = {}
                err_msg = (
                    f"[service-affecting-monitor-reports] Reports could not be generated for client: {client_id}. "
                    f"No tickets were found."
                )
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
            affecting_tickets_per_client[client_id] = tickets

        await self._service_affecting_monitor_report(
            affecting_tickets_per_client=affecting_tickets_per_client,
            customer_cache=customer_cache,
            cached_names_by_serial=cached_names_by_serial,
            trailing_interval=trailing_interval,
        )

        monitor_report_end_time = datetime.utcnow()
        self._logger.info(
            f"[service-affecting-monitor-reports] Reports generation finished. "
            f"Took {round((monitor_report_end_time - monitor_report_init_time).total_seconds() / 60, 2)} minutes."
        )

    async def _service_affecting_monitor_report(
        self, affecting_tickets_per_client, cached_names_by_serial, customer_cache, trailing_interval
    ):

        self._logger.info(f"Generating all reports for {len(affecting_tickets_per_client)} Bruin clients...")

        active_reports = self._config.MONITOR_REPORT_CONFIG["active_reports"]
        client_names_by_id = self.get_clients_names_and_ids_for_client(customer_cache)

        threshold = self._config.MONITOR_REPORT_CONFIG["threshold"]
        for client_id, affecting_tickets in affecting_tickets_per_client.items():
            await asyncio.sleep(0)

            ticket_details_by_serial = self.get_ticket_details_for_serial_and_trouble(
                active_reports, affecting_tickets, cached_names_by_serial, client_id
            )
            report_list = self._bruin_repository.prepare_items_for_monitor_report(
                ticket_details_by_serial, cached_names_by_serial
            )

            final_report_list = self._bruin_repository.filter_trouble_reports(
                active_reports=active_reports, report_list=report_list, threshold=threshold
            )
            final_report_list.sort(key=lambda item: item["serial_number"])

            if self._config.CURRENT_ENVIRONMENT != "production":
                self._logger.info(
                    f"No report for client {client_id} will be sent as the current environment is for environments "
                    f"different that production"
                )
                continue

            email = self._template_repository.compose_monitor_report_email(
                client_id=client_id,
                client_name=client_names_by_id[client_id],
                report_items=final_report_list,
                trailing_interval=trailing_interval,
            )

            await self._email_repository.send_email(email_object=email)

            self._logger.info(f"Report for client {client_id} sent via email")

    def get_ticket_details_for_serial_and_trouble(
        self, active_reports, affecting_tickets, cached_names_by_serial, client_id
    ):
        self._logger.info(f"[service-affecting-monitor-reports] Starting all report for client {client_id}")
        ticket_details = self._bruin_repository.transform_tickets_into_ticket_details(affecting_tickets)
        filtered_ticket_details = self._bruin_repository.filter_ticket_details_by_serials(
            ticket_details, cached_names_by_serial
        )
        filtered_ticket_details = self._bruin_repository.filter_trouble_notes_in_ticket_details(
            filtered_ticket_details, active_reports
        )
        ticket_details_by_serial = self._bruin_repository.group_ticket_details_by_serial(filtered_ticket_details)
        return ticket_details_by_serial

    @staticmethod
    def get_clients_names_and_ids_for_client(customer_cache):
        return {
            edge["bruin_client_info"]["client_id"]: edge["bruin_client_info"]["client_name"] for edge in customer_cache
        }

    @staticmethod
    def get_rounded_date(date):
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    def get_trailing_interval_for_date(self, date):
        return {
            "start": date - timedelta(days=self._config.MONITOR_REPORT_CONFIG["trailing_days"]),
            "end": date,
        }

    @staticmethod
    def get_format_to_string_date(datetime_value):
        return datetime_value.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def get_serial_and_name_for_cached_edges_with_client_id(customer_cache, clients_id):
        serials_and_name = {}

        for cached_info in customer_cache:
            if (
                cached_info["bruin_client_info"]["client_id"] in clients_id
                and cached_info["serial_number"] not in serials_and_name
            ):
                serials_and_name[cached_info["serial_number"]] = cached_info["edge_name"]

        return serials_and_name
