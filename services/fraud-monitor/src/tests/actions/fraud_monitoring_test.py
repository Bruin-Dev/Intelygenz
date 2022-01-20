import pytest
from unittest.mock import Mock
from unittest.mock import patch

from shortuuid import uuid
from datetime import datetime
from apscheduler.util import undefined
from apscheduler.jobstores.base import ConflictingIdError

from application.actions import fraud_monitoring as fraud_monitor_module
from application.repositories import bruin_repository as bruin_repository_module
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, 'uuid', return_value=uuid_)

config_mock = patch.object(testconfig, 'CURRENT_ENVIRONMENT', 'production')


class TestFraudMonitor:
    def instance_test(self, fraud_monitor, event_bus, logger, scheduler, notifications_repository,
                      bruin_repository, ticket_repository):
        assert fraud_monitor._event_bus == event_bus
        assert fraud_monitor._logger == logger
        assert fraud_monitor._scheduler == scheduler
        assert fraud_monitor._config == testconfig
        assert fraud_monitor._notifications_repository == notifications_repository
        assert fraud_monitor._bruin_repository == bruin_repository
        assert fraud_monitor._ticket_repository == ticket_repository

    @pytest.mark.asyncio
    async def start_fraud_monitoring__success_test(self, fraud_monitor, scheduler):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(fraud_monitor_module, 'datetime', new=datetime_mock):
            await fraud_monitor.start_fraud_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            fraud_monitor._fraud_monitoring_process, 'interval',
            minutes=testconfig.FRAUD_CONFIG['monitoring_interval'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_fraud_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_fraud_monitoring__conflict_test(self, fraud_monitor, scheduler):
        job_id = '_fraud_monitor_process'
        scheduler.add_job.side_effect = ConflictingIdError(job_id)

        await fraud_monitor.start_fraud_monitoring()

        scheduler.add_job.assert_called_once_with(
            fraud_monitor._fraud_monitoring_process, 'interval',
            minutes=testconfig.FRAUD_CONFIG['monitoring_interval'],
            next_run_time=undefined,
            replace_existing=False,
            id=job_id
        )

    @pytest.mark.asyncio
    async def fraud_monitoring_process__invalid_email_test(self, fraud_monitor, make_email):
        email = make_email(message=None)

        response = {
            'body': [email],
            'status': 200,
        }

        fraud_monitor._notifications_repository.get_unread_emails.return_value = response

        await fraud_monitor._fraud_monitoring_process()
        fraud_monitor._process_fraud.assert_not_called()

    @pytest.mark.asyncio
    async def fraud_monitoring_process__not_fraud_email_test(self, fraud_monitor, make_email):
        email = make_email()

        response = {
            'body': [email],
            'status': 200,
        }

        fraud_monitor._notifications_repository.get_unread_emails.return_value = response

        await fraud_monitor._fraud_monitoring_process()
        fraud_monitor._process_fraud.assert_not_called()

    @pytest.mark.asyncio
    async def fraud_monitoring_process__unexpected_email_body_test(self, fraud_monitor, make_email):
        email = make_email(subject='Possible Fraud on 12345678')

        response = {
            'body': [email],
            'status': 200,
        }

        fraud_monitor._notifications_repository.get_unread_emails.return_value = response

        await fraud_monitor._fraud_monitoring_process()
        fraud_monitor._process_fraud.assert_not_called()

    @pytest.mark.asyncio
    async def fraud_monitoring_process__email_processed_test(self, fraud_monitor, make_email):
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        email = make_email(
            msg_uid=msg_uid,
            body=body,
            subject='Possible Fraud on 12345678',
        )

        get_unread_emails_response = {
            'body': [email],
            'status': 200,
        }

        mark_email_as_read_response = {
            'body': None,
            'status': 204,
        }

        fraud_monitor._notifications_repository.get_unread_emails.return_value = get_unread_emails_response
        fraud_monitor._notifications_repository.mark_email_as_read.return_value = mark_email_as_read_response
        fraud_monitor._process_fraud.return_value = True

        with config_mock:
            await fraud_monitor._fraud_monitoring_process()

        fraud_monitor._process_fraud.assert_called_once_with(body, msg_uid)
        fraud_monitor._notifications_repository.mark_email_as_read.assert_called_once_with(msg_uid)

    @pytest.mark.asyncio
    async def fraud_monitoring_process__email_not_processed_test(self, fraud_monitor, make_email):
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        email = make_email(
            msg_uid=msg_uid,
            body=body,
            subject='Possible Fraud on 12345678',
        )

        get_unread_emails_response = {
            'body': [email],
            'status': 200,
        }

        fraud_monitor._notifications_repository.get_unread_emails.return_value = get_unread_emails_response
        fraud_monitor._process_fraud.return_value = False

        await fraud_monitor._fraud_monitoring_process()

        fraud_monitor._process_fraud.assert_called_once_with(body, msg_uid)
        fraud_monitor._notifications_repository.mark_email_as_read.assert_not_called()

    @pytest.mark.asyncio
    async def process_fraud__append_note_to_ticket_test(
            self, fraud_monitor, make_ticket, make_detail_item_with_notes_and_ticket_info,
            make_get_client_info_by_did_response, make_get_tickets_response):
        service_number = ''
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
        )

        full_body = (
            'Network,\n'
            '\n'
            f'{body}\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        ticket = make_ticket()
        detail_info = make_detail_item_with_notes_and_ticket_info()

        fraud_monitor._bruin_repository.get_client_info_by_did.return_value = make_get_client_info_by_did_response()
        fraud_monitor._bruin_repository.get_open_fraud_tickets.return_value = make_get_tickets_response(ticket)
        fraud_monitor._get_oldest_fraud_ticket.return_value = detail_info

        await fraud_monitor._process_fraud(full_body, msg_uid)

        fraud_monitor._append_note_to_ticket.assert_awaited_once_with(detail_info, service_number, body, msg_uid)

    @pytest.mark.asyncio
    async def process_fraud__reopen_resolved_ticket_test(
            self, fraud_monitor, make_ticket, make_detail_item_with_notes_and_ticket_info,
            make_get_client_info_by_did_response, make_get_tickets_response):
        service_number = ''
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
        )

        full_body = (
            'Network,\n'
            '\n'
            f'{body}\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        ticket = make_ticket()
        detail_info = make_detail_item_with_notes_and_ticket_info()

        fraud_monitor._bruin_repository.get_client_info_by_did.return_value = make_get_client_info_by_did_response()
        fraud_monitor._bruin_repository.get_open_fraud_tickets.return_value = make_get_tickets_response(ticket)
        fraud_monitor._get_oldest_fraud_ticket.return_value = detail_info
        fraud_monitor._ticket_repository.is_task_resolved.return_value = True

        await fraud_monitor._process_fraud(full_body, msg_uid)

        fraud_monitor._unresolve_task_for_ticket.assert_awaited_once_with(detail_info, service_number, body, msg_uid)

    @pytest.mark.asyncio
    async def process_fraud__reopen_closed_ticket_test(
            self, fraud_monitor, make_ticket, make_detail_item_with_notes_and_ticket_info,
            make_get_client_info_by_did_response, make_get_tickets_response):
        service_number = ''
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
        )

        full_body = (
            'Network,\n'
            '\n'
            f'{body}\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        ticket = make_ticket()
        detail_info = make_detail_item_with_notes_and_ticket_info()

        fraud_monitor._bruin_repository.get_client_info_by_did.return_value = make_get_client_info_by_did_response()
        fraud_monitor._bruin_repository.get_open_fraud_tickets.return_value = make_get_tickets_response()
        fraud_monitor._bruin_repository.get_resolved_fraud_tickets.return_value = make_get_tickets_response(ticket)
        fraud_monitor._get_oldest_fraud_ticket.side_effect = [None, detail_info]

        await fraud_monitor._process_fraud(full_body, msg_uid)

        fraud_monitor._unresolve_task_for_ticket.assert_awaited_once_with(detail_info, service_number, body, msg_uid)

    @pytest.mark.asyncio
    async def process_fraud__create_ticket_test(
            self, fraud_monitor, make_get_client_info_by_did_response, make_get_tickets_response):
        client_id = 0
        service_number = ''
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
        )

        full_body = (
            'Network,\n'
            '\n'
            f'{body}\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        fraud_monitor._bruin_repository.get_client_info_by_did.return_value = make_get_client_info_by_did_response()
        fraud_monitor._bruin_repository.get_open_fraud_tickets.return_value = make_get_tickets_response()
        fraud_monitor._bruin_repository.get_resolved_fraud_tickets.return_value = make_get_tickets_response()

        await fraud_monitor._process_fraud(full_body, msg_uid)

        fraud_monitor._create_fraud_ticket.assert_awaited_once_with(client_id, service_number, body, msg_uid)

    @pytest.mark.asyncio
    async def process_fraud__create_ticket__default_client_info_test(
            self, fraud_monitor, make_get_tickets_response, bruin_500_response):
        default_client_info = testconfig.FRAUD_CONFIG['default_client_info']
        client_id = default_client_info['client_id']
        service_number = default_client_info['service_number']
        msg_uid = '123456'

        body = (
            'Possible Fraud Warning with the following information:\n'
            'DID: 12345678\n'
        )

        full_body = (
            'Network,\n'
            '\n'
            f'{body}\n'
            '\n'
            'Thanks,\n'
            'Fraud Detection System'
        )

        fraud_monitor._bruin_repository.get_client_info_by_did.return_value = bruin_500_response
        fraud_monitor._bruin_repository.get_open_fraud_tickets.return_value = make_get_tickets_response()
        fraud_monitor._bruin_repository.get_resolved_fraud_tickets.return_value = make_get_tickets_response()

        await fraud_monitor._process_fraud(full_body, msg_uid)

        fraud_monitor._create_fraud_ticket.assert_awaited_once_with(client_id, service_number, body, msg_uid)

    @pytest.mark.asyncio
    async def get_oldest_fraud_ticket__found_test(
            self, fraud_monitor, make_ticket, make_detail_item, make_ticket_note, make_ticket_details,
            make_detail_item_with_notes_and_ticket_info, make_rpc_response):
        service_number = 'VC1234567'

        ticket = make_ticket()
        tickets = [ticket]

        detail_item = make_detail_item(value=service_number)
        detail_items = [detail_item]

        note = make_ticket_note(text="#*MetTel's IPA*#\nPossible Fraud Warning", service_numbers=[service_number])
        notes = [note]

        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        fraud_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await fraud_monitor._get_oldest_fraud_ticket(tickets, service_number)
        expected = make_detail_item_with_notes_and_ticket_info(detail_item=detail_item, notes=notes, ticket_info=ticket)
        assert result == expected

    @pytest.mark.asyncio
    async def get_oldest_fraud_ticket__not_found_test(
            self, fraud_monitor, make_ticket, make_detail_item, make_ticket_note, make_ticket_details,
            make_rpc_response):
        service_number = 'VC1234567'

        ticket = make_ticket()
        tickets = [ticket]

        detail_item = make_detail_item(value=service_number)
        detail_items = [detail_item]

        note = make_ticket_note(service_numbers=[service_number])
        notes = [note]

        ticket_details = make_ticket_details(detail_items=detail_items, notes=notes)

        fraud_monitor._bruin_repository.get_ticket_details.return_value = make_rpc_response(
            body=ticket_details,
            status=200,
        )

        result = await fraud_monitor._get_oldest_fraud_ticket(tickets, service_number)
        assert result is None

    @pytest.mark.asyncio
    async def append_note_to_ticket__note_already_exists_test(
            self, fraud_monitor, make_detail_item_with_notes_and_ticket_info):
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        detail_info = make_detail_item_with_notes_and_ticket_info()

        fraud_monitor._ticket_repository.note_already_exists.return_value = True
        result = await fraud_monitor._append_note_to_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()
        assert result is True

    @pytest.mark.asyncio
    async def append_note_to_ticket__not_production_test(
            self, fraud_monitor, make_detail_item_with_notes_and_ticket_info):
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        detail_info = make_detail_item_with_notes_and_ticket_info()

        result = await fraud_monitor._append_note_to_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.append_note_to_ticket.assert_not_awaited()
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()
        assert result is True

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_has_not_2xx_status_test(
            self, fraud_monitor, make_ticket, make_detail_item_with_notes_and_ticket_info, make_rpc_response):
        ticket_id = 11111
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        ticket = make_ticket(ticket_id=ticket_id)
        detail_info = make_detail_item_with_notes_and_ticket_info(ticket_info=ticket)

        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = make_rpc_response(
            body=None,
            status=400,
        )

        with config_mock:
            result = await fraud_monitor._append_note_to_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, service_number,
                                                                                       email_body, msg_uid)
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_success_test(
            self, fraud_monitor, make_ticket, make_detail_item_with_notes_and_ticket_info,
            bruin_generic_200_response):
        ticket_id = 11111
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        ticket = make_ticket(ticket_id=ticket_id)
        detail_info = make_detail_item_with_notes_and_ticket_info(ticket_info=ticket)

        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with config_mock:
            result = await fraud_monitor._append_note_to_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, service_number,
                                                                                       email_body, msg_uid)
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_awaited_once_with(ticket_id,
                                                                                                       service_number)
        assert result is True

    @pytest.mark.asyncio
    async def unresolve_task_for_ticket__not_production_test(
            self, fraud_monitor, make_detail_item_with_notes_and_ticket_info):
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        detail_info = make_detail_item_with_notes_and_ticket_info()

        result = await fraud_monitor._unresolve_task_for_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.open_ticket.assert_not_awaited()
        fraud_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        assert result is True

    @pytest.mark.asyncio
    async def unresolve_task_for_ticket__open_ticket_rpc_request_has_not_2xx_status_test(
            self, fraud_monitor, make_ticket, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            bruin_500_response):
        ticket_id = 11111
        task_id = 22222
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        ticket = make_ticket(ticket_id=ticket_id)
        detail_item = make_detail_item(id_=task_id)
        detail_info = make_detail_item_with_notes_and_ticket_info(ticket_info=ticket, detail_item=detail_item)

        fraud_monitor._bruin_repository.open_ticket.return_value = bruin_500_response

        with config_mock:
            result = await fraud_monitor._unresolve_task_for_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, task_id)
        fraud_monitor._notifications_repository.notify_successful_reopen.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def unresolve_task_for_ticket__open_ticket_rpc_request_success__append_note_rpc_request_has_not_2xx_status_test(  # noqa
            self, fraud_monitor, make_ticket, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            bruin_generic_200_response, bruin_500_response):
        ticket_id = 11111
        task_id = 22222
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        ticket = make_ticket(ticket_id=ticket_id)
        detail_item = make_detail_item(id_=task_id)
        detail_info = make_detail_item_with_notes_and_ticket_info(ticket_info=ticket, detail_item=detail_item)

        fraud_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_500_response

        with config_mock:
            result = await fraud_monitor._unresolve_task_for_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, task_id)
        fraud_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once_with(ticket_id,
                                                                                                  service_number)
        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, service_number, email_body, msg_uid, reopening=True
        )
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def unresolve_task_for_ticket__open_ticket_rpc_request_success__append_note_rpc_request_success_test(
            self, fraud_monitor, make_ticket, make_detail_item, make_detail_item_with_notes_and_ticket_info,
            bruin_generic_200_response):
        ticket_id = 11111
        task_id = 22222
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        ticket = make_ticket(ticket_id=ticket_id)
        detail_item = make_detail_item(id_=task_id)
        detail_info = make_detail_item_with_notes_and_ticket_info(ticket_info=ticket, detail_item=detail_item)

        fraud_monitor._bruin_repository.open_ticket.return_value = bruin_generic_200_response
        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with config_mock:
            result = await fraud_monitor._unresolve_task_for_ticket(detail_info, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.open_ticket.assert_awaited_once_with(ticket_id, task_id)
        fraud_monitor._notifications_repository.notify_successful_reopen.assert_awaited_once_with(ticket_id,
                                                                                                  service_number)
        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, service_number, email_body, msg_uid, reopening=True
        )
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_awaited_once_with(ticket_id,
                                                                                                       service_number)
        assert result is True

    @pytest.mark.asyncio
    async def create_fraud_ticket__no_contacts_test(self, fraud_monitor):
        client_id = 12345
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        fraud_monitor._get_contacts.return_value = None

        result = await fraud_monitor._create_fraud_ticket(client_id, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.create_fraud_ticket.assert_not_awaited()
        fraud_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def create_fraud_ticket__not_production_test(self, fraud_monitor, make_contact_info):
        client_id = 12345
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'

        fraud_monitor._get_contacts.return_value = make_contact_info()

        result = await fraud_monitor._create_fraud_ticket(client_id, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.create_fraud_ticket.assert_not_awaited()
        fraud_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        assert result is True

    @pytest.mark.asyncio
    async def create_fraud_ticket__create_ticket_rpc_request_has_not_2xx_status_test(
            self, fraud_monitor, make_contact_info, make_rpc_response):
        client_id = 12345
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'
        contacts = make_contact_info()

        fraud_monitor._get_contacts.return_value = make_contact_info()
        fraud_monitor._bruin_repository.create_fraud_ticket.return_value = make_rpc_response(
            body=None,
            status=400,
        )

        with config_mock:
            result = await fraud_monitor._create_fraud_ticket(client_id, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.create_fraud_ticket.assert_awaited_once_with(client_id, service_number,
                                                                                     contacts)
        fraud_monitor._notifications_repository.notify_successful_ticket_creation.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def create_fraud_ticket__create_ticket_rpc_request_success__append_note_rpc_request_has_not_2xx_status_test(
            self, fraud_monitor, make_contact_info, make_create_ticket_200_response, bruin_500_response):
        ticket_id = 11111
        client_id = 12345
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'
        contacts = make_contact_info()

        fraud_monitor._get_contacts.return_value = make_contact_info()
        fraud_monitor._bruin_repository.create_fraud_ticket.return_value = make_create_ticket_200_response(
            ticket_id=ticket_id
        )
        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_500_response

        with config_mock:
            result = await fraud_monitor._create_fraud_ticket(client_id, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.create_fraud_ticket.assert_awaited_once_with(client_id, service_number,
                                                                                     contacts)
        fraud_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once_with(
            ticket_id, service_number
        )
        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, service_number,
                                                                                       email_body, msg_uid)
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_not_awaited()
        assert result is False

    @pytest.mark.asyncio
    async def create_fraud_ticket__create_ticket_rpc_request_success__append_note_rpc_request_success_test(
            self, fraud_monitor, make_contact_info, make_create_ticket_200_response, bruin_generic_200_response):
        ticket_id = 11111
        client_id = 12345
        service_number = 'VC1234567'
        msg_uid = '123456'
        email_body = 'Possible Fraud Warning'
        contacts = make_contact_info()

        fraud_monitor._get_contacts.return_value = make_contact_info()
        fraud_monitor._bruin_repository.create_fraud_ticket.return_value = make_create_ticket_200_response(
            ticket_id=ticket_id
        )
        fraud_monitor._bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        with config_mock:
            result = await fraud_monitor._create_fraud_ticket(client_id, service_number, email_body, msg_uid)

        fraud_monitor._bruin_repository.create_fraud_ticket.assert_awaited_once_with(client_id, service_number,
                                                                                     contacts)
        fraud_monitor._notifications_repository.notify_successful_ticket_creation.assert_awaited_once_with(
            ticket_id, service_number
        )
        fraud_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, service_number,
                                                                                       email_body, msg_uid)
        fraud_monitor._notifications_repository.notify_successful_note_append.assert_awaited_once_with(ticket_id,
                                                                                                       service_number)
        assert result is True

    @pytest.mark.asyncio
    async def get_contacts__client_info_rpc_request__has_not_2xx_status_test(
            self, fraud_monitor, make_contact_info, bruin_500_response):
        client_id = 12345
        service_number = 'VC1234567'
        contacts = make_contact_info()

        fraud_monitor._bruin_repository.get_client_info.return_value = bruin_500_response

        result = await fraud_monitor._get_contacts(client_id, service_number)

        fraud_monitor._bruin_repository.get_client_info.assert_awaited_once_with(service_number)
        fraud_monitor._bruin_repository.get_site_details.assert_not_awaited()
        fraud_monitor._bruin_repository.get_contact_info.assert_not_called()
        assert fraud_monitor._bruin_repository.get_contacts.call_count == 1
        assert result == contacts

    @pytest.mark.asyncio
    async def get_contacts__client_info_rpc_request_success__site_details_rpc_request_has_not_2xx_status_test(
            self, fraud_monitor, make_contact_info, make_get_client_info_200_response, bruin_500_response):
        site_id = 11111
        client_id = 12345
        service_number = 'VC1234567'
        contacts = make_contact_info()

        fraud_monitor._bruin_repository.get_client_info.return_value = make_get_client_info_200_response(
            site_id=site_id)
        fraud_monitor._bruin_repository.get_site_details.return_value = bruin_500_response

        result = await fraud_monitor._get_contacts(client_id, service_number)

        fraud_monitor._bruin_repository.get_client_info.assert_awaited_once_with(service_number)
        fraud_monitor._bruin_repository.get_site_details.assert_awaited_once_with(client_id, site_id)
        fraud_monitor._bruin_repository.get_contact_info.assert_not_called()
        assert fraud_monitor._bruin_repository.get_contacts.call_count == 1
        assert result == contacts

    @pytest.mark.asyncio
    async def get_contacts__client_info_rpc_request_success__site_details_rpc_request_success_test(
            self, fraud_monitor, make_contact_info, make_get_client_info_200_response,
            make_get_site_details_200_response):
        site_id = 11111
        client_id = 12345
        service_number = 'VC1234567'

        contact = {'name': 'Test contact', 'email': 'contact@test.com'}
        contacts = make_contact_info(**contact)

        fraud_monitor._bruin_repository.get_client_info.return_value = make_get_client_info_200_response(
            site_id=site_id)
        fraud_monitor._bruin_repository.get_site_details.return_value = make_get_site_details_200_response(
            contact=contact
        )

        result = await fraud_monitor._get_contacts(client_id, service_number)

        fraud_monitor._bruin_repository.get_client_info.assert_awaited_once_with(service_number)
        fraud_monitor._bruin_repository.get_site_details.assert_awaited_once_with(client_id, site_id)
        fraud_monitor._bruin_repository.get_contact_info.assert_called_once()
        assert fraud_monitor._bruin_repository.get_contacts.call_count == 2
        assert result == contacts
