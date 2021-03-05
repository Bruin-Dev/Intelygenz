from datetime import datetime
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest
from asynctest import CoroutineMock
from shortuuid import uuid

from application.actions import new_tickets_monitor as new_tickets_monitor_module
from application.actions.new_tickets_monitor import NewTicketsMonitor
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(new_tickets_monitor_module, 'uuid', return_value=uuid_)


class TestNewTicketsMonitor:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_tickets_repository = Mock()
        email_tagger_repository = Mock()
        new_tickets_monitor = NewTicketsMonitor(event_bus, logger, scheduler, config, new_tickets_repository,
                                                email_tagger_repository, bruin_repository)

        assert new_tickets_monitor._event_bus is event_bus
        assert new_tickets_monitor._logger is logger
        assert new_tickets_monitor._scheduler is scheduler
        assert new_tickets_monitor._config is config
        assert new_tickets_monitor._bruin_repository is bruin_repository
        assert new_tickets_monitor._email_tagger_repository is email_tagger_repository
        assert new_tickets_monitor._new_tickets_repository is new_tickets_repository

    @pytest.mark.asyncio
    async def start_new_tickets_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_tickets_repository = Mock()
        email_tagger_repository = Mock()
        new_tickets_monitor = NewTicketsMonitor(event_bus, logger, scheduler, config, new_tickets_repository,
                                                email_tagger_repository, bruin_repository)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(new_tickets_monitor_module, 'datetime', new=datetime_mock):
            with patch.object(new_tickets_monitor_module, 'timezone', new=Mock()):
                await new_tickets_monitor.start_ticket_events_monitor(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            new_tickets_monitor._run_new_tickets_polling, 'interval',
            seconds=testconfig.MONITOR_CONFIG['scheduler_config']['new_tickets_seconds'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_new_tickets_polling',
        )

    @pytest.mark.asyncio
    async def new_tickets_monitor_process_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_tickets_repository = Mock()
        email_tagger_repository = Mock()
        new_tickets_monitor = NewTicketsMonitor(event_bus, logger, scheduler, config, new_tickets_repository,
                                                email_tagger_repository, bruin_repository)

        pending_tickets = [
            {'email': {'email': {'email_id': '100', 'client_id': '333'}}, 'ticket': {'ticket_id': 200}},
            {'email': {'email': {'email_id': '101', 'client_id': '333'}}, 'ticket': {'ticket_id': 201}},
        ]

        ticket_basic_info = {'ticket_id': 444, 'ticket_type': 'BIL'}

        new_tickets_monitor._new_tickets_repository.get_pending_tickets = Mock(return_value=pending_tickets)
        new_tickets_monitor._email_tagger_repository.save_metrics = CoroutineMock(return_value={'status': 200})
        new_tickets_monitor._bruin_repository.get_single_ticket_basic_info = CoroutineMock(return_value={
            'status': 200,
            'body': ticket_basic_info
        })
        new_tickets_monitor._new_tickets_repository.mark_complete = Mock()

        await new_tickets_monitor._run_new_tickets_polling()

        new_tickets_monitor._email_tagger_repository.save_metrics.assert_has_awaits([
            call(pending_tickets[0]['email'], ticket_basic_info),
            call(pending_tickets[1]['email'], ticket_basic_info),
        ], any_order=True)
        new_tickets_monitor._new_tickets_repository.mark_complete.assert_has_calls([
            call(pending_tickets[0]['email']['email']['email_id'], pending_tickets[0]['ticket']['ticket_id']),
            call(pending_tickets[1]['email']['email']['email_id'], pending_tickets[1]['ticket']['ticket_id'])
        ], any_order=True)
        new_tickets_monitor._bruin_repository.get_single_ticket_basic_info.assert_has_awaits([
            call(pending_tickets[0]['ticket']['ticket_id']),
            call(pending_tickets[1]['ticket']['ticket_id'])
        ], any_order=True)

    @pytest.mark.asyncio
    async def _save_metrics_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_tickets_repository = Mock()
        email_tagger_repository = Mock()
        new_tickets_monitor = NewTicketsMonitor(event_bus, logger, scheduler, config, new_tickets_repository,
                                                email_tagger_repository, bruin_repository)

        email_id = "100"
        ticket_id = 200
        client_id = 300
        email_data = {'email': {'email_id': email_id, 'client_id': client_id}}
        ticket_data = {'ticket_id': '200'}
        ticket_basic_info = {'ticket_id': ticket_id, 'ticket_type': 'BIL'}

        new_tickets_monitor._email_tagger_repository.save_metrics = CoroutineMock(return_value={'status': 200})
        new_tickets_monitor._bruin_repository.get_single_ticket_basic_info = CoroutineMock(return_value={
            'status': 200,
            'body': ticket_basic_info
        })
        new_tickets_monitor._new_tickets_repository.mark_complete = Mock()

        await new_tickets_monitor._save_metrics(email_data, ticket_data)

        new_tickets_monitor._bruin_repository.get_single_ticket_basic_info.assert_awaited_once_with(ticket_id)
        new_tickets_monitor._email_tagger_repository.save_metrics.assert_awaited_once_with(email_data,
                                                                                           ticket_basic_info)
        new_tickets_monitor._new_tickets_repository.mark_complete.assert_called_once_with(email_id, ticket_id)
