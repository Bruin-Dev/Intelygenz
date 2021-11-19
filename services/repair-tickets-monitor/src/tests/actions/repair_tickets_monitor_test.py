from asynctest import CoroutineMock
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from config import testconfig as config


class TestRepairTicketsMonitor:
    def instance_test(
        self,
        event_bus,
        logger,
        scheduler,
        new_tagged_emails_repository,
        repair_ticket_kre_repository,
    ):
        repair_tickets_monitor = RepairTicketsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            new_tagged_emails_repository,
            repair_ticket_kre_repository,
        )

        assert repair_tickets_monitor._event_bus == event_bus
        assert repair_tickets_monitor._logger == logger
        assert repair_tickets_monitor._scheduler == scheduler
        assert repair_tickets_monitor._config == config
        assert repair_tickets_monitor._new_tagged_emails_repository == new_tagged_emails_repository
        assert repair_tickets_monitor._repair_tickets_kre_repository == repair_ticket_kre_repository

    @pytest.mark.asyncio
    async def start_repair_tickets_monitor__exec_on_start_test(self, repair_tickets_monitor, scheduler):
        next_run_time = datetime.now()

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch('application.actions.repair_tickets_monitor.datetime', datetime_mock):
            await repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            repair_tickets_monitor._run_repair_tickets_polling,
            'interval',
            seconds=config.MONITOR_CONFIG['scheduler_config']['repair_ticket_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_repair_tickets_polling'
        )

    def _triage_emails_by_tag_test(self, repair_tickets_monitor):
        tagged_emails = [{'email_id': 1234, 'tag_id': 1}, {'email_id': 1234, 'tag_id': 2}]

        repair_emails, other_emails = repair_tickets_monitor._triage_emails_by_tag(tagged_emails)

        assert list(repair_emails)[0] == tagged_emails[0]
        assert list(other_emails)[0] == tagged_emails[1]

    @pytest.mark.asyncio
    async def _get_inference__ok_test(self, repair_tickets_monitor, make_rpc_response):
        email_data = {}
        prediction_data = {'predicted_class': 'test'}
        rpc_reponse = make_rpc_response(status=200, body=prediction_data)
        repair_tickets_kre_repository = CoroutineMock()
        repair_tickets_kre_repository.get_email_inference = CoroutineMock(return_value=rpc_reponse)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email_data)

        assert response == prediction_data

    @pytest.mark.asyncio
    async def _get_inference__400_test(self, repair_tickets_monitor, make_rpc_response):
        email_data = {}
        rpc_reponse = make_rpc_response(status=400, body='Error in data')
        repair_tickets_kre_repository = CoroutineMock()
        repair_tickets_kre_repository.get_email_inference = CoroutineMock(return_value=rpc_reponse)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email_data)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once(
            email_data
        )
        assert response is None

    @pytest.mark.asyncio
    async def _process_other_tags_email_test(self, repair_tickets_monitor, make_email):
        email_id = 1234
        email = {'email_id': email_id}

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository

        await repair_tickets_monitor._process_other_tags_email(email)

        new_tagged_emails_repository.mark_complete.assert_called_once_with(email_id)

    async def _process_repair_email_test(self):
        # TODO when this method is finished test when there are more parts
        pass
