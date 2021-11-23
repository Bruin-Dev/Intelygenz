from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

import pytest

from apscheduler.events import EVENT_JOB_ERROR, JobExecutionEvent
from apscheduler.util import undefined
from asynctest import CoroutineMock
from pytz import timezone

from application.actions import billing_report as alert_module
from application.actions.billing_report import BillingReport
from config.testconfig import BILLING_REPORT_CONFIG

from application.repositories.template_renderer import TemplateRenderer


@pytest.fixture
def lumin_repo_responses():
    return [
        {
            "conversation_id": "5735605401026560",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
            "timestamp": "2019-02-24T21:29:36.798081+00:00",
            "type": "billing.scheduled"
        },
        {
            "conversation_id": "5711381785477120",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
            "timestamp": "2019-02-24T21:36:01.295808+00:00",
            "type": "billing.scheduled"
        },
        {
            "conversation_id": "5735605401026560",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
            "timestamp": "2019-02-24T21:29:36.798081+00:00",
            "type": "billing.rescheduled"
        },
        {
            "conversation_id": "5711381785477120",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
            "timestamp": "2019-02-24T21:36:01.295808+00:00",
            "type": "billing.rescheduled"
        }
    ]


@pytest.fixture
def summary():
    today = date.today()
    last = date.today() - timedelta(days=1)
    first = last.replace(day=1)

    return {
        "dates": {
            "current": today.strftime(BILLING_REPORT_CONFIG["date_format"]),
            "start": first.strftime(BILLING_REPORT_CONFIG["date_format"]),
            "end": last.strftime(BILLING_REPORT_CONFIG["date_format"])
        },
        "customer": BILLING_REPORT_CONFIG["customer_name"],
        "total_api_uses": 4,
        "type_counts": {
            "billing.scheduled": 2,
            "billing.rescheduled": 2
        }
    }


class TestBillingReport:

    def instance_test(self):
        email_client = Mock()
        lumin_repo = Mock()
        templ = TemplateRenderer(BILLING_REPORT_CONFIG)
        scheduler = Mock()

        opts = {
            "logger": Mock(),
            "config": BILLING_REPORT_CONFIG
        }

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)

        assert report._email_client is email_client
        assert report._lumin_repo is lumin_repo
        assert report._scheduler is scheduler
        assert report._logger is opts["logger"]
        assert report._config is opts["config"]

    def start_billing_report_job_with_exec_on_start_test(self):
        opts = {
            "logger": Mock(),
            "config": BILLING_REPORT_CONFIG
        }

        email_client = Mock()
        lumin_repo = Mock()
        templ = Mock()
        scheduler = Mock()

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(alert_module, 'datetime', new=datetime_mock):
            with patch.object(alert_module, 'timezone', new=Mock()):
                report.start_billing_report_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            report._billing_report_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=next_run_time,
            replace_existing=True,
            id='_billing_report_process',
        )

    def start_billing_report_job_with_no_exec_on_start_test(self):
        opts = {
            "logger": Mock(),
            "config": BILLING_REPORT_CONFIG
        }

        email_client = Mock()
        lumin_repo = Mock()
        templ = Mock()
        scheduler = Mock()

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)
        report.start_billing_report_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            report._billing_report_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=undefined,
            replace_existing=True,
            id='_billing_report_process',
        )

    def register_error_handler_test(self):
        opts = {
            "logger": Mock(),
            "config": BILLING_REPORT_CONFIG
        }

        email_client = Mock()
        lumin_repo = Mock()
        templ = Mock()
        scheduler = Mock()

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)
        report.register_error_handler()

        scheduler.add_listener.assert_called_with(report._event_listener, EVENT_JOB_ERROR)

    def event_listener_test(self):
        logger = Mock()

        opts = {
            "logger": logger,
            "config": BILLING_REPORT_CONFIG
        }

        email_client = Mock()
        lumin_repo = Mock()
        templ = Mock()
        scheduler = Mock()

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)

        mock_event = JobExecutionEvent(
            code=None,
            job_id=report.JOB_ID,
            jobstore=None,
            scheduled_run_time=None,
            exception=Exception("Test exception")
        )

        report._event_listener(mock_event)

        logger.exception.assert_called_with('Execution failed for billing report', mock_event.exception)
        logger.exception.reset_mock()

        mock_event.job_id = "foo"

        report._event_listener(mock_event)

        logger.exception.assert_not_called()

    @pytest.mark.asyncio
    async def billing_process_test(self, lumin_repo_responses, summary):
        email_contents = {'email': "<div>Some email</div>"}

        email_client = Mock()
        email_client.send_to_email = CoroutineMock()
        lumin_repo = Mock()
        lumin_repo.get_billing_data_for_period = CoroutineMock(return_value=lumin_repo_responses)
        scheduler = Mock()
        templ = Mock()
        templ.compose_email_object = Mock(return_value=email_contents)

        opts = {
            "logger": Mock(),
            "config": BILLING_REPORT_CONFIG
        }

        report = BillingReport(lumin_repo, email_client, templ, scheduler, **opts)

        await report._billing_report_process()

        lumin_repo.get_billing_data_for_period.assert_called()

        repo_args = lumin_repo.get_billing_data_for_period.call_args[0]

        start_date = repo_args[1]
        end_date = repo_args[2]

        assert start_date.day == 1
        assert start_date < end_date

        assert start_date.tzinfo.zone == BILLING_REPORT_CONFIG["timezone"]
        assert end_date.tzinfo.zone == BILLING_REPORT_CONFIG["timezone"]

        tz = timezone(BILLING_REPORT_CONFIG["timezone"])
        now = tz.localize(datetime.now())

        assert end_date < now

        template_args = templ.compose_email_object.call_args[0]

        assert template_args[0] == summary
        assert template_args[1] == lumin_repo_responses
