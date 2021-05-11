from datetime import datetime, timedelta
from typing import Set

from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from igz.packages.eventbus.eventbus import EventBus

from application.repositories.bruin_repository import BruinRepository


class ServiceAffectingMonitorReports:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, bruin_repository,
                 notifications_repository, customer_cache_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository
        self._ISO_8601_FORMAT_UTC = "%Y-%m-%dT%H:%M:%SZ"
        self._customer_cache_repository = customer_cache_repository

        self.__reset_state()

    async def monitor_reports(self):
        self.__reset_state()
        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        self._customer_cache: list = customer_cache_response['body']
        if not self._customer_cache:
            err_msg = '[service-affecting-monitor-reports] Got an empty customer cache. Process cannot keep going.'
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return
        self._clients_id: Set[int] = set(edge['bruin_client_info']['client_id'] for edge in self._customer_cache)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self._config.MONITOR_REPORT_CONFIG['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date_str = start_date.strftime(self._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(self._ISO_8601_FORMAT_UTC)
        for client_id in self._clients_id:
            tickets = await self._bruin_repository.get_affecting_ticket_for_report(client_id,
                                                                                   start_date_str,
                                                                                   end_date_str)
            if not tickets:
                err_msg = \
                    f"[service-affecting-monitor-reports] Reports could not be generated for client: {client_id}. " \
                    f"No tickets were found."
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
                continue
            self._affecting_tickets_per_client[client_id] = tickets
        if not self._affecting_tickets_per_client:
            err_msg = '[service-affecting-monitor-reports] No tickets available at any customer.'
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return
        await self._service_affecting_monitor_report()

    def __reset_state(self):
        self._customer_cache = []
        self._affecting_tickets_per_client = {}
        self._clients_id = {}

    async def start_service_affecting_monitor_reports_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting monitor reports')

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now the process of creation reports')
            self._scheduler.add_job(self.monitor_reports, 'interval',
                                    minutes=self._config.MONITOR_REPORT_CONFIG["monitoring_minutes_interval"],
                                    next_run_time=next_run_time,
                                    replace_existing=True,
                                    id=f"_monitor_reports")
        else:
            self._scheduler.add_job(self.monitor_reports,
                                    CronTrigger.from_crontab(self._config.MONITOR_REPORT_CONFIG["crontab"],
                                                             timezone=timezone('UTC')),
                                    id=f"_monitor_reports", replace_existing=True)

    async def _service_affecting_monitor_report(self):
        self._logger.info(f"Generating all reports for {len(self._affecting_tickets_per_client)} Bruin clients...")

        start = datetime.now()
        serial_numbers: Set[str] = set(edge['serial_number'] for edge in self._customer_cache)
        active_reports = self._config.MONITOR_REPORT_CONFIG['active_reports']
        client_name_by_id = {
            edge['bruin_client_info']['client_id']: edge['bruin_client_info']['client_name']
            for edge in self._customer_cache
        }

        threshold = self._config.MONITOR_REPORT_CONFIG['threshold']
        for client_id, affecting_tickets in self._affecting_tickets_per_client.items():
            self._logger.info(f"[service-affecting-monitor-reports] Starting all report for client {client_id}")
            ticket_details = self._bruin_repository.transform_tickets_into_ticket_details(affecting_tickets)

            filtered_ticket_details = self._bruin_repository.filter_ticket_details_by_serials(
                ticket_details,
                serial_numbers)

            filtered_ticket_details = self._bruin_repository.filter_trouble_notes_in_ticket_details(
                filtered_ticket_details,
                active_reports)

            ticket_details_by_serial = self._bruin_repository.group_ticket_details_by_serial(
                filtered_ticket_details)
            report_list = self._bruin_repository.prepare_items_for_report(ticket_details_by_serial)

            final_report_list = [item for item in report_list if item['number_of_tickets'] >= threshold]

            if not final_report_list:
                self._logger.info(
                    f"No report for client {client_id} will be sent as there is no info "
                    f"to put in the report"
                )
                continue

            working_environment = self._config.MONITOR_REPORT_CONFIG['environment']
            if working_environment != 'production':
                self._logger.info(
                    f"No report for client {client_id} will be sent as the current environment is "
                    f"{working_environment.upper()}")
                continue

            email = self._template_renderer.compose_email_report_object(
                report_items=final_report_list,
                client_name=client_name_by_id[client_id],
                client_id=client_id,
            )
            if email:
                await self._notifications_repository.send_email(email_object=email)

            self._logger.info(f"Report for client {client_id} sent via email")

            end = datetime.now()
            self._logger.info(
                f"[service-affecting-monitor-reports] Reports generation for client {client_id} finished. "
                f"Took {round((end - start).total_seconds() / 60, 2)} minutes.")
