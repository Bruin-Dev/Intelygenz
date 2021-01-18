from datetime import datetime, timedelta
from datetime import timezone as tz

from apscheduler.triggers.cron import CronTrigger
from apscheduler.util import undefined
from pytz import timezone

from igz.packages.eventbus.eventbus import EventBus

from application.repositories.bruin_repository import BruinRepository


class ServiceAffectingMonitorReports:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, bruin_repository,
                 notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self._ISO_8601_FORMAT_UTC = "%Y-%m-%dT%H:%M:%SZ"

    def _get_report_function(self, report):
        switcher = {
            'bandwitdh_over_utilization': self._service_affecting_monitor_report_bandwidth_over_utilization
        }
        return switcher.get(report.get('type'), None)

    async def start_service_affecting_monitor_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service affecting')

        if exec_on_start:
            for report in self._config.MONITOR_REPORT_CONFIG['reports']:
                next_run_time = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
                self._logger.info(f'It will be executed now')
                self._scheduler.add_job(self._get_report_function(report), 'interval',
                                        minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                                        next_run_time=next_run_time,
                                        replace_existing=True,
                                        args=[report],
                                        id=f"_monitor_reports_{report['type']}")
        else:
            for report in self._config.MONITOR_REPORT_CONFIG['reports']:
                self._logger.info(f"It will be executed at {report['crontab']}")
                self._logger.info(f"- Setting up report '{report['name']}' of type '{report['type']}'"
                                  f" with params: \n {report}")
                self._scheduler.add_job(self._get_report_function(report),
                                        CronTrigger.from_crontab(report['crontab'], timezone=timezone('UTC')),
                                        args=[report], id=f"_monitor_reports_{report['type']}")

    async def _service_affecting_monitor_report_bandwidth_over_utilization(self, report):
        self._logger.info(f"Running report: {report}")
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)
        start_date = end_date - timedelta(days=report['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date_str = start_date.strftime(self._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(self._ISO_8601_FORMAT_UTC)
        start = datetime.now()
        self._logger.info(f"[service-affecting-monitor-reports] Starting report")

        affecting_tickets = await self._bruin_repository.get_affecting_ticket_for_report(report, start_date_str,
                                                                                         end_date_str)
        if not affecting_tickets:
            self._logger.error(f"[service-affecting-monitor-reports] Report could not be generated."
                               f"We could not retrieve all tickets.")
            return
        filtered_affecting_tickets = BruinRepository.find_bandwidth_over_utilization_tickets(affecting_tickets,
                                                                                             self.MAIN_WATERMARK)

        mapped_serials_tickets = self._bruin_repository.map_tickets_with_serial_numbers(filtered_affecting_tickets)

        final_report_list = self._bruin_repository.prepare_items_for_report(mapped_serials_tickets)

        # Last filter - number of tickets greater than 3
        final_report_list = [item for item in final_report_list if item['number_of_tickets'] > report['threshold']]

        end = datetime.now() - start
        if len(final_report_list) > 0:
            email_object = self._template_renderer.compose_email_bandwidth_over_utilization_report_object(
                report=report, report_items=final_report_list)
            await self._notifications_repository.send_email(email_object=email_object)
            self._logger.info(f"[service-affecting-monitor-reports] Report sended by email")
        else:
            self._logger.info(f"[service-affecting-monitor-reports] Report not needed to send, there are no items")

        self._logger.info(f"[service-affecting-monitor-reports] Report finished took {end}")
