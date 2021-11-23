from collections import defaultdict
from datetime import date, datetime, time, timedelta

from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from pytz import timezone

from application.clients.email_client import EmailClient
from application.repositories.template_renderer import TemplateRenderer
from application.repositories.lumin_repository import LuminBillingRepository
from application.repositories.lumin_repository import LuminBillingTypes


class BillingReport:

    JOB_ID = '_billing_report_process'

    def __init__(
            self,
            lumin_repo: LuminBillingRepository,
            email_client: EmailClient,
            template_renderer: TemplateRenderer,
            scheduler: AsyncIOScheduler,
            **opts):
        self._lumin_repo = lumin_repo
        self._email_client = email_client
        self._template_renderer = template_renderer
        self._scheduler = scheduler
        self._logger = opts.get("logger")
        self._config = opts.get("config")

    def start_billing_report_job(self, exec_on_start=False):
        self._logger.info("Scheduled task: billing report process configured to run first day of each month")

        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config['timezone']))
            self._logger.info(f'It will be executed now')

        self._scheduler.add_job(
            self._billing_report_process, 'cron',
            day=1,
            misfire_grace_time=86400,
            replace_existing=True,
            next_run_time=next_run_time,
            id=self.JOB_ID)

    def register_error_handler(self):
        self._scheduler.add_listener(self._event_listener, EVENT_JOB_ERROR)

    def _event_listener(self, event: JobExecutionEvent):
        if event.job_id != self.JOB_ID:
            return

        self._logger.exception('Execution failed for billing report', event.exception)
        self.start_billing_report_job(exec_on_start=True)

    async def generate_billing_report_data(self):
        tz = timezone(self._config["timezone"])

        billing_types = [LuminBillingTypes.ALL.value]
        last = tz.localize(datetime.combine(date.today(), time.max) - timedelta(days=1))
        first = tz.localize(datetime.combine(last.date(), time.min).replace(day=1))

        summary = {
            "dates": {
                "current": date.today().strftime(self._config["date_format"]),
                "start": first.strftime(self._config["date_format"]),
                "end": last.strftime(self._config["date_format"])
            },
            "customer": self._config["customer_name"],
            "total_api_uses": 0,
            "type_counts": defaultdict(int)
        }

        items = await self._lumin_repo.get_billing_data_for_period(billing_types, first, last)
        for item in items:
            summary["total_api_uses"] += 1
            summary["type_counts"][item["type"]] += 1

        return self._template_renderer.compose_email_object(summary, items)

    async def _billing_report_process(self):
        self._logger.info("Requesting lumin.AI usage details for billing report")

        email_obj = await self.generate_billing_report_data()
        self._email_client.send_to_email(email_obj)

        self._logger.info("Lumin.AI Billing Report sent")
