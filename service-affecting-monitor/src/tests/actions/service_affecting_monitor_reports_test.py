from datetime import datetime, timedelta
from datetime import timezone as tz
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from apscheduler.triggers.cron import CronTrigger
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import service_affecting_monitor_reports as service_affecting_monitor_module
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(service_affecting_monitor_module, 'uuid', return_value=uuid_)


class TestServiceAffectingMonitorReports:

    def instance_test(
            self, event_bus, logger, scheduler, template_renderer, bruin_repository, notifications_repository,
            customer_cache_repository):
        config = testconfig
        service_affecting_monitor_reports = ServiceAffectingMonitorReports(
            event_bus, logger, scheduler, config, template_renderer, bruin_repository, notifications_repository,
            customer_cache_repository
        )

        assert service_affecting_monitor_reports._event_bus is event_bus
        assert service_affecting_monitor_reports._logger is logger
        assert service_affecting_monitor_reports._scheduler is scheduler
        assert service_affecting_monitor_reports._config is config
        assert service_affecting_monitor_reports._template_renderer is template_renderer
        assert service_affecting_monitor_reports._bruin_repository is bruin_repository
        assert service_affecting_monitor_reports._notifications_repository is notifications_repository
        assert service_affecting_monitor_reports._customer_cache_repository is customer_cache_repository

    def get_report_function_test(self, service_affecting_monitor_reports, report):
        assert service_affecting_monitor_reports._get_report_function(report) == \
               service_affecting_monitor_reports._service_affecting_monitor_report_bandwidth_over_utilization

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_with_exec_on_start_test(self, service_affecting_monitor_reports,
                                                                          report, response_customer_cache):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        service_affecting_monitor_reports._customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=response_customer_cache)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(service_affecting_monitor_module, 'timezone', new=Mock()):
                await service_affecting_monitor_reports.start_service_affecting_monitor_job(exec_on_start=True)

        service_affecting_monitor_reports._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor_reports._get_report_function(report), 'interval',
            minutes=testconfig.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=True,
            args=[report],
            id=f"_monitor_reports_{report['type']}",
        )

    @pytest.mark.asyncio
    async def start_service_affecting_monitor_job_with_no_exec_on_start_test(self, service_affecting_monitor_reports,
                                                                             report, response_customer_cache):
        crontab_value = CronTrigger.from_crontab(report['crontab'])
        crontab_mock = Mock(return_value=crontab_value)
        service_affecting_monitor_reports._customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=response_customer_cache)
        with patch.object(CronTrigger, 'from_crontab', new=crontab_mock):
            await service_affecting_monitor_reports.start_service_affecting_monitor_job(exec_on_start=False)

        service_affecting_monitor_reports._scheduler.add_job.assert_called_once_with(
            service_affecting_monitor_reports._get_report_function(report), crontab_value, args=[report],
            id=f"_monitor_reports_{report['type']}")

    @pytest.mark.asyncio
    async def service_affecting_monitor_report_bandwidth_over_utilization_test(self, service_affecting_monitor_reports,
                                                                               report, response_bruin_with_all_tickets,
                                                                               response_mapped_tickets,
                                                                               response_prepare_items_for_report,
                                                                               response_customer_cache,
                                                                               filtered_affecting_tickets):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)
        start_date = end_date - timedelta(days=report['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date_str = start_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock(
            side_effect=[response_bruin_with_all_tickets]
        )
        service_affecting_monitor_reports._bruin_repository.group_ticket_details_by_serial = Mock(
            return_value=response_mapped_tickets
        )
        service_affecting_monitor_reports._bruin_repository.prepare_items_for_report = Mock(
            return_value=response_prepare_items_for_report)
        service_affecting_monitor_reports._template_renderer.compose_email_report_object = \
            Mock()
        service_affecting_monitor_reports._notifications_repository.send_email = CoroutineMock()

        service_affecting_monitor_reports._customer_cache = response_customer_cache['body']
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports._service_affecting_monitor_report_bandwidth_over_utilization(report)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_awaited_once_with(
            report, start_date_str, end_date_str)
        service_affecting_monitor_reports._bruin_repository.group_ticket_details_by_serial.assert_called_once_with(
            filtered_affecting_tickets)
        service_affecting_monitor_reports._bruin_repository.prepare_items_for_report.assert_called_once_with(
            response_mapped_tickets)
        service_affecting_monitor_reports._template_renderer.compose_email_report_object. \
            assert_called_once()
        service_affecting_monitor_reports._notifications_repository.send_email.assert_awaited_once()

    @pytest.mark.asyncio
    async def report_bandwidth_over_utilization_no_cache_test(self, report,
                                                              service_affecting_monitor_reports,
                                                              response_empty_customer_cache):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock()
        service_affecting_monitor_reports._customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=response_empty_customer_cache)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports.start_service_affecting_monitor_job(True)
        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_not_awaited()

    @pytest.mark.asyncio
    async def report_bandwidth_over_utilization_bad_response_cache_test(self,
                                                                        service_affecting_monitor_reports,
                                                                        response_bad_status_customer_cache):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock()
        service_affecting_monitor_reports._customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=response_bad_status_customer_cache)
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports.start_service_affecting_monitor_job(True)
        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_not_awaited()

    @pytest.mark.asyncio
    async def service_affecting_monitor_report_bandwidth_over_utilization_no_items_for_report_test(
            self, service_affecting_monitor_reports, report, response_bruin_with_all_tickets):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)
        start_date = end_date - timedelta(days=report['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date_str = start_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._customer_cache = []
        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock(
            side_effect=[response_bruin_with_all_tickets]
        )
        service_affecting_monitor_reports._template_renderer.compose_email_bandwidth_over_utilization_report_object = \
            Mock()
        service_affecting_monitor_reports._notifications_repository.send_email = CoroutineMock()

        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports._service_affecting_monitor_report_bandwidth_over_utilization(report)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_awaited_once_with(
            report, start_date_str, end_date_str)
        service_affecting_monitor_reports._template_renderer.compose_email_bandwidth_over_utilization_report_object. \
            assert_not_called()
        service_affecting_monitor_reports._notifications_repository.send_email.assert_not_awaited()

    @pytest.mark.asyncio
    async def service_affecting_monitor_report_bandwidth_over_utilization_with_exception_test(
            self, service_affecting_monitor_reports, report, response_bruin_with_all_tickets_with_exception,
            response_customer_cache):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)
        start_date = end_date - timedelta(days=report['trailing_days'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date_str = start_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)
        end_date_str = end_date.strftime(service_affecting_monitor_reports._ISO_8601_FORMAT_UTC)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock(
            side_effect=[response_bruin_with_all_tickets_with_exception]
        )
        service_affecting_monitor_reports._bruin_repository.map_ticket_details_and_notes_with_serial_numbers = Mock()
        service_affecting_monitor_reports._bruin_repository.prepare_items_for_report = Mock()
        service_affecting_monitor_reports._template_renderer.compose_email_bandwidth_over_utilization_report_object = \
            Mock()
        service_affecting_monitor_reports._notifications_repository.send_email = CoroutineMock()
        service_affecting_monitor_reports._customer_cache_repository.get_cache_for_affecting_monitoring = CoroutineMock(
            return_value=response_customer_cache)

        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports._service_affecting_monitor_report_bandwidth_over_utilization(report)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_awaited_once_with(
            report, start_date_str, end_date_str)
        service_affecting_monitor_reports._bruin_repository.map_ticket_details_and_notes_with_serial_numbers \
            .assert_not_called()
        service_affecting_monitor_reports._bruin_repository.prepare_items_for_report.assert_not_called()
        service_affecting_monitor_reports._template_renderer.compose_email_bandwidth_over_utilization_report_object. \
            assert_not_called()
        service_affecting_monitor_reports._notifications_repository.send_email.assert_not_called()

    @pytest.mark.asyncio
    async def service_affecting_monitor_reports_utilization_with_exception_test(
            self, report_jitter, service_affecting_monitor_reports,
            response_bruin_with_all_tickets,
            response_customer_cache):
        end_date = datetime.utcnow().replace(tzinfo=tz.utc)

        datetime_mock = Mock()
        datetime_mock.utcnow = Mock(return_value=end_date)
        datetime_mock.now = Mock(return_value=end_date)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report = CoroutineMock(
            return_value=response_bruin_with_all_tickets
        )
        service_affecting_monitor_reports._notifications_repository.send_email = CoroutineMock()

        service_affecting_monitor_reports._customer_cache = response_customer_cache['body']
        with patch.object(service_affecting_monitor_module, 'datetime', new=datetime_mock):
            await service_affecting_monitor_reports._service_affecting_monitor_report_by_serial(report_jitter)

        service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report.assert_awaited()
        service_affecting_monitor_reports._notifications_repository.send_email.assert_awaited()
