import pytest
from shortuuid import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock
from unittest.mock import patch
from asynctest import CoroutineMock

from application.actions import alert as alert_module
from application.actions.alert import Alert
from apscheduler.util import undefined

from config import testconfig

from application.repositories.template_management import TemplateRenderer
from unittest.mock import call

uuid_ = uuid()
uuid_mock = patch.object(alert_module, 'uuid', return_value=uuid_)


class TestAlert:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        velocloud_repository = Mock()
        template_renderer = TemplateRenderer(config.ALERTS_CONFIG)
        notifications_repository = Mock()

        alert = Alert(event_bus, scheduler, logger, config, velocloud_repository, template_renderer,
                      notifications_repository)
        assert alert._event_bus is event_bus
        assert alert._scheduler is scheduler
        assert alert._logger is logger
        assert alert._config is config
        assert alert._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def start_alert_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        template_renderer = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()

        alert = Alert(event_bus, scheduler, logger, testconfig, velocloud_repository, template_renderer,
                      notifications_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(alert_module, 'datetime', new=datetime_mock):
            with patch.object(alert_module, 'timezone', new=Mock()):
                await alert.start_alert_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            alert._alert_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=next_run_time,
            replace_existing=True,
            id='_alert_process',
        )

    @pytest.mark.asyncio
    async def start_alert_job_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        scheduler.add_job = Mock()
        template_renderer = Mock()
        velocloud_repository = Mock()
        notifications_repository = Mock()

        alert = Alert(event_bus, scheduler, logger, testconfig, velocloud_repository, template_renderer,
                      notifications_repository)
        await alert.start_alert_job(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            alert._alert_process, 'cron',
            day=1, misfire_grace_time=86400,
            next_run_time=undefined,
            replace_existing=True,
            id='_alert_process',
        )

    @pytest.mark.asyncio
    async def alert_process_test(self, alert, edge_link_list, email_obj, list_edge_alert):
        alert._velocloud_repository.get_edges = CoroutineMock(return_value=edge_link_list)
        alert._event_bus.publish_message = CoroutineMock(return_value=None)
        datetime_mock = Mock()
        datetime_now = datetime.now()
        datetime_mock.now = Mock(return_value=datetime_now)
        datetime_mock.strptime = Mock(return_value=datetime_now - timedelta(days=40))
        alert._template_renderer.compose_email_object = Mock(return_value=email_obj)
        alert._notifications_repository.send_email = CoroutineMock()
        with patch.object(alert_module, 'datetime', new=datetime_mock) as _:
            await alert._alert_process()

        alert._template_renderer.compose_email_object.assert_called_once_with(list_edge_alert)
        alert._notifications_repository.send_email.assert_awaited_once_with(email_obj)

    @pytest.mark.asyncio
    async def alert_process_empty_test(self, alert, email_obj, list_edge_alert):
        alert._velocloud_repository.get_edges = CoroutineMock(return_value=[])
        alert._event_bus.publish_message = CoroutineMock(return_value=None)
        datetime_mock = Mock()
        datetime_now = datetime.now()
        datetime_mock.now = Mock(return_value=datetime_now)
        datetime_mock.strptime = Mock(return_value=datetime_now - timedelta(days=40))
        alert._template_renderer.compose_email_object = Mock(return_value=email_obj)
        alert._notifications_repository.send_email = CoroutineMock()
        with patch.object(alert_module, 'datetime', new=datetime_mock) as _:
            await alert._alert_process()
        alert._notifications_repository.send_email.assert_not_awaited()

    @pytest.mark.asyncio
    async def alert_process_not_elapsed_last_contact_test(self, alert, edge_link_list, email_obj, list_edge_alert):
        alert._velocloud_repository.get_edges = CoroutineMock(return_value=edge_link_list)
        alert._event_bus.publish_message = CoroutineMock(return_value=None)
        datetime_mock = Mock()
        datetime_now = datetime.now()
        datetime_mock.now = Mock(return_value=datetime_now)
        late_date = datetime_now - timedelta(days=40)
        datetime_mock.strptime = Mock(side_effect=[datetime_now, late_date, late_date, late_date])
        alert._template_renderer.compose_email_object = Mock(return_value=email_obj)
        alert._notifications_repository.send_email = CoroutineMock()
        with patch.object(alert_module, 'datetime', new=datetime_mock) as _:
            await alert._alert_process()
        alert._template_renderer.compose_email_object.assert_called_once_with(
            [list_edge_alert[1], list_edge_alert[2], list_edge_alert[3]])
        alert._notifications_repository.send_email.assert_awaited_once_with(email_obj)
