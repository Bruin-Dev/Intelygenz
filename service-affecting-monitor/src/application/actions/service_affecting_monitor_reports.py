import time
from datetime import datetime, timedelta
from datetime import timezone as tz

from apscheduler.triggers.cron import CronTrigger
from apscheduler.util import undefined
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
        await self.__reset_state()
        if len(self._affecting_tickets.keys()) > 0 and len(self._customer_cache) > 0:
            for report in self._config.MONITOR_REPORT_CONFIG['reports']:
                await self._service_affecting_monitor_report(report)

    async def __reset_state(self):
        self._customer_cache = []
        self._affecting_tickets = {}
        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        response_status = customer_cache_response['status']
        if response_status not in range(200, 300) or response_status == 202:
            err_msg = f"[service-affecting-monitor-reports] status {response_status} calling customer cache. " \
                      f"Can't continue creating report"
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return
        self._customer_cache: list = customer_cache_response['body']
        if not self._customer_cache:
            err_msg = '[service-affecting-monitor-reports] Got an empty customer cache. Process cannot keep going.'
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return
        set_cache_clients_id = set(edge['bruin_client_info']['client_id'] for edge in self._customer_cache)
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)
        start_date = end_date - timedelta(days=self._config.MONITOR_REPORT_CONFIG['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date_str = start_date.strftime(self._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(self._ISO_8601_FORMAT_UTC)
        for client_id in list(set_cache_clients_id):
            tickets = await self._bruin_repository.get_affecting_ticket_for_report(client_id,
                                                                                   start_date_str,
                                                                                   end_date_str)
            if not tickets:
                err_msg = f"[service-affecting-monitor-reports] Report could not be generated fot one client."
                f"We could not retrieve all tickets for client_id: {client_id}"
                self._logger.error(err_msg)
                await self._notifications_repository.send_slack_message(err_msg)
                continue
            self._affecting_tickets[client_id] = tickets

    async def start_service_affecting_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting')

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now the process of creation reports')
            self._scheduler.add_job(self.monitor_reports, 'interval',
                                    minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                                    next_run_time=next_run_time,
                                    replace_existing=True,
                                    id=f"_monitor_reports")
        else:
            self._scheduler.add_job(self.monitor_reports,
                                    CronTrigger.from_crontab('0 8 * * *', timezone=timezone('UTC')),
                                    id=f"_monitor_reports")

    async def _service_affecting_monitor_report(self, report):
        self._logger.info(f"Running report: {report['value']}")

        start = datetime.now()
        set_cache_serials = set(edge['serial_number'] for edge in self._customer_cache)
        set_cache_clients_id = set(edge['bruin_client_info']['client_id'] for edge in self._customer_cache)
        for client_id in list(set_cache_clients_id):
            if client_id in self._affecting_tickets:
                self._logger.info(f"[service-affecting-monitor-reports] Starting {report['value']} report")
                transformed_tickets = BruinRepository.transform_tickets_into_ticket_details(
                    self._affecting_tickets[client_id])

                filtered_affecting_tickets = BruinRepository.filter_tickets_with_serial_cached(transformed_tickets,
                                                                                               set_cache_serials)

                filtered_affecting_tickets = BruinRepository.filter_trouble_notes(filtered_affecting_tickets,
                                                                                  report['value'])

                mapped_serials_tickets = self._bruin_repository.group_ticket_details_by_serial(
                    filtered_affecting_tickets)

                if report['type'] == 'bandwidth_utilization':
                    report_list = self._bruin_repository.prepare_items_for_report(mapped_serials_tickets)
                else:
                    report_list = self._bruin_repository.prepare_items_for_report_by_interface(mapped_serials_tickets)

                final_report_list = [item for item in report_list if item['number_of_tickets'] > report['threshold']]

                end = datetime.now() - start
                if len(final_report_list) > 0:
                    email_object = self._template_renderer.compose_email_report_object(
                        report=report, report_items=final_report_list)
                    await self._notifications_repository.send_email(email_object=email_object)
                    self._logger.info(f"[service-affecting-monitor-reports] Report {report['value']} sended by email")
                else:
                    self._logger.info(
                        f"[service-affecting-monitor-reports] Report {report['value']} "
                        f"not needed to send, there are no items")

                self._logger.info(f"[service-affecting-monitor-reports] Report {report['value']} finished took {end}")
