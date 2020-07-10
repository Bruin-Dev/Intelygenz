import copy
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import pytest

from asynctest import CoroutineMock
from pytz import timezone
from shortuuid import uuid

from application.repositories import cts_repository as cts_repository_module
from application.repositories import nats_error_response
from application.repositories.cts_repository import CtsRepository
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note

from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(cts_repository_module, 'uuid', return_value=uuid_)


class TestCtsRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        cts_repository = CtsRepository(logger, config, event_bus, notifications_repository, bruin_repository)

        assert cts_repository._event_bus is event_bus
        assert cts_repository._logger is logger
        assert cts_repository._config is config
        assert cts_repository._notifications_repository is notifications_repository
        assert cts_repository._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_all_dispatches_test(self, cts_repository, cts_dispatch, cts_dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': {
                "done": True,
                "totalSize": 2,
                "records": [
                    cts_dispatch,
                    cts_dispatch_confirmed
                ]
            },
            'status': 200,
        }
        cts_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        with uuid_mock:
            result = await cts_repository.get_all_dispatches()
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_failing_test(self, cts_repository):

        request = {
            'request_id': uuid_,
            'body': {},
        }

        cts_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        cts_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await cts_repository.get_all_dispatches()

        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        cts_repository._notifications_repository.send_slack_message.assert_awaited_once()
        cts_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_dispatches_error_non_2xx_status_test(self, cts_repository, cts_dispatch, cts_dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': 'Error',
            'status': 500,
        }
        cts_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        cts_repository._notifications_repository.send_slack_message = CoroutineMock()
        with uuid_mock:
            result = await cts_repository.get_all_dispatches()
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=30)
        cts_repository._notifications_repository.send_slack_message.assert_awaited_once()
        cts_repository._logger.error.assert_called_once()
        assert result == response

    def get_sms_to_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        expected_phone = '+12027723610'
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_error_no_contact_test(self, cts_dispatch_confirmed_no_contact):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_no_contact)
        expected_phone = None
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_error_number_test(self, cts_dispatch_confirmed_error_number):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_error_number)
        expected_phone = None
        assert CtsRepository.get_sms_to(updated_dispatch) == expected_phone

    def is_valid_ticket_id_test(self):
        valid_ticket_id = '4663397'
        invalid_ticket_id_1 = '4663397|IW24654081'
        invalid_ticket_id_2 = '712637/IW76236'
        invalid_ticket_id_3 = '123-3123'
        invalid_ticket_id_4 = '4485610(Order)/4520284(Port)'
        assert CtsRepository.is_valid_ticket_id(ticket_id=valid_ticket_id) is True
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_1) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_2) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_3) is False
        assert CtsRepository.is_valid_ticket_id(ticket_id=invalid_ticket_id_4) is False

    def is_dispatch_confirmed_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_not_confirmed):
        assert cts_dispatch_monitor._cts_repository.is_dispatch_confirmed(cts_dispatch_confirmed) is True
        assert cts_dispatch_monitor._cts_repository.is_dispatch_confirmed(cts_dispatch_not_confirmed) is False

    def is_tech_on_site_test(self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_not_on_site):
        assert cts_dispatch_monitor._cts_repository.is_tech_on_site(cts_dispatch_tech_on_site) is True
        assert cts_dispatch_monitor._cts_repository.is_tech_on_site(cts_dispatch_tech_not_on_site) is False

    def get_dispatches_splitted_by_status_test(self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed,
                                               cts_dispatch_confirmed_2, cts_dispatch_tech_on_site,
                                               cts_bad_status_dispatch):
        dispatches = [
            cts_dispatch, cts_dispatch_confirmed, cts_dispatch_confirmed_2,
            cts_dispatch_tech_on_site, cts_bad_status_dispatch
        ]
        expected_dispatches_splitted = {
            str(cts_dispatch_monitor._cts_repository.DISPATCH_REQUESTED): [cts_dispatch],
            str(cts_dispatch_monitor._cts_repository.DISPATCH_CONFIRMED): [
                cts_dispatch_confirmed, cts_dispatch_confirmed_2],
            str(cts_dispatch_monitor._cts_repository.DISPATCH_FIELD_ENGINEER_ON_SITE): [cts_dispatch_tech_on_site],
            str(cts_dispatch_monitor._cts_repository.DISPATCH_REPAIR_COMPLETED): [],
            str(cts_dispatch_monitor._cts_repository.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL): []
        }
        result = cts_dispatch_monitor._cts_repository.get_dispatches_splitted_by_status(dispatches)
        assert result == expected_dispatches_splitted

    @pytest.mark.asyncio
    async def append_confirmed_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'
        note_data = {
            'vendor': 'CTS',
            'dispatch_number': igz_dispatch_number,
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'tech_name': cts_dispatch_confirmed.get('API_Resource_Name__c'),
            'tech_phone': cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        }
        note = cts_get_dispatch_confirmed_note(note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._cts_repository.append_confirmed_note(
            dispatch_number, igz_dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'

        note_data = {
            'vendor': 'CTS',
            'dispatch_number': igz_dispatch_number,
            'date_of_dispatch': cts_dispatch_confirmed.get('Local_Site_Time__c'),
            'tech_name': cts_dispatch_confirmed.get('API_Resource_Name__c'),
            'tech_phone': cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        }
        note = cts_get_dispatch_confirmed_note(note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f'An error occurred when appending a confirmed note with bruin client. ' \
                  f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_confirmed_note(
            dispatch_number, igz_dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+16666666666'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._cts_repository.append_confirmed_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+16666666666'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                  f"- SMS Confirmed note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_confirmed_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_confirmed_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+16666666666'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_tech_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        response = await cts_dispatch_monitor._cts_repository.append_confirmed_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_tech_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        dispatch_number = cts_dispatch_confirmed['Name']
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+16666666666'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_tech_note(sms_note_data)
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_to_ticket_mock])
        err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                  f"- Tech SMS Confirmed note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_confirmed_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_12_sms_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 12h prior reminder SMS sent to +1987654327\n'
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_tech_12_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_12_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 12h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS 12 hours note not appended'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_tech_12_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_12_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 12h prior reminder tech SMS sent to +1987654327\n'
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_12_sms_tech_note_error_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 12h prior reminder tech SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 12 hours note not appended'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_tech_12_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 2h prior reminder SMS sent to +1987654327\n'
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_tech_2_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_2_sms_note_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 2h prior reminder SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS 2 hours note not appended'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_tech_2_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_2_sms_tech_note_test(self, cts_dispatch_monitor, cts_dispatch, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 2h prior reminder tech SMS sent to +1987654327\n'
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_2_sms_tech_note_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch 2h prior reminder tech SMS sent to +1987654327\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech 2 hours note not appended'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_tech_2_sms_tech_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Dispatch_Number')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\nDispatch Management - Field Engineer On Site\n' \
                   f'SMS notification sent to +1987654327\n\n' \
                   f'The field engineer, Michael J. Fox has arrived.\n'
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to,
            cts_dispatch_confirmed.get('API_Resource_Name__c'))

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                      append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\n' \
                   f'Dispatch Management - Field Engineer On Site\n' \
                   f'SMS notification sent to +1987654327\n\nThe field engineer, Michael J. Fox has arrived.\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech on site note not appended'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_tech_on_site_sms_note(
            dispatch_number, igz_dispatch_number, ticket_id, sms_to, cts_dispatch_confirmed.get('API_Resource_Name__c'))

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def send_confirmed_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from LIT',
            'status': 500,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending Confirmed SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_dispatch_confirmed_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from LIT',
            'status': 500,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_dispatch_confirmed_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        request = {
            'request_id': uuid_,
            'body': sms_payload,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending Confirmed SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_12_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_12_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_12_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 12 hours SMS with notifier ' \
                                           f'client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_tech_12_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_12_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+12123595129'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_tech_12_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data,
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 12 hours SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_12_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_2_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_2_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 2 hours SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_2_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_tech_2_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_2_sms_tech_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech(
            dispatch_number, ticket_id, updated_dispatch, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_2_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')

        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = '+12123595129'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_tech_2_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech 2 hours SMS tech ' \
                                           f'with notifier client. payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_2_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': cts_dispatch_confirmed.get('API_Resource_Name__c')
        }

        sms_data = cts_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await cts_dispatch_monitor._cts_repository.send_tech_on_site_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        sms_to = None

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_on_site_sms(
            dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': cts_dispatch_confirmed.get('API_Resource_Name__c')
        }

        sms_data = cts_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        send_error_sms_to_slack_response = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                           f'An error occurred when sending a tech on site SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_tech_on_site_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
