import copy
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
from unittest.mock import call

import iso8601
import pytest
import pytz

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
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms

from application.templates.cts.sms.updated_tech import cts_get_updated_tech_sms, cts_get_updated_tech_sms_tech
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
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=60)
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

        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=60)
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
        cts_repository._event_bus.rpc_request.assert_awaited_once_with("cts.dispatch.get", request, timeout=60)
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

    def get_sms_to_from_note_test(self):
        note = "#*Automation Engine*# IGZ57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Location ID: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Phone: (202) 772-3610\n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_phone = '+12027723610'
        assert CtsRepository.get_sms_to_from_note(note) == expected_phone

    def get_sms_to_from_note_error_no_contact_test(self):
        note = "#*Automation Engine*# IGZ57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Location ID: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Phone: NO CONTACT\n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_phone = None
        assert CtsRepository.get_sms_to_from_note(note) == expected_phone

    def get_sms_to_from_note_error_number_test(self):
        note = "#*Automation Engine*# IGZ57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Location ID: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Phone: (7) \n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_phone = None
        assert CtsRepository.get_sms_to_from_note(note) == expected_phone

    def get_sms_to_from_note_error_not_phone_lines_test(self):
        note = "#*Automation Engine*# IGZ57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Location ID: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_phone = None
        assert CtsRepository.get_sms_to_from_note(note) == expected_phone

    def get_sms_to_from_note_with_note_none_test(self):
        note = None
        expected_phone = None
        assert CtsRepository.get_sms_to_from_note(note) == expected_phone

    def get_onsite_contact_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        expected_phone = 'Manager On Duty'
        assert CtsRepository.get_onsite_contact(updated_dispatch) == expected_phone

    def get_onsite_contact_no_contact_test(self, cts_dispatch_confirmed_no_contact_name):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_no_contact_name)
        expected_phone = None
        assert CtsRepository.get_onsite_contact(updated_dispatch) == expected_phone

    def get_onsite_contact_from_note_test(self):
        note = "#*Automation Engine*# DIS57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Address: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Phone: (7) \n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_name = 'MOD manager'
        assert CtsRepository.get_onsite_contact_from_note(note) == expected_name

    def get_onsite_contact_from_note_none_note_test(self):
        note = None
        expected_name = None
        assert CtsRepository.get_onsite_contact_from_note(note) == expected_name

    def get_onsite_contact_from_note_no_contact_test(self):
        note = "#*Automation Engine*# DIS57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Address: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "NO_CONTACT: MOD manager\n" \
               "Phone: (7) \n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_name = None
        assert CtsRepository.get_onsite_contact_from_note(note) == expected_name

    def get_location_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        expected = '750 S Federal Hwy , Pompano Beach, Florida, 33062'
        assert CtsRepository.get_location(updated_dispatch) == expected

    def get_location_no_location_test(self, cts_dispatch_confirmed_no_address):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed_no_address)
        expected_phone = None
        assert CtsRepository.get_location(updated_dispatch) == expected_phone

    def get_location_from_note_with_address_test(self):
        note = "#*Automation Engine*# DIS57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "Address: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "On-Site Contact: MOD manager\n" \
               "Phone: (7) \n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected_name = '750 S Federal Hwy , Pompano Beach, Florida, 33062'
        assert CtsRepository.get_location_from_note(note) == expected_name

    def get_location_from_note_none_note_test(self):
        note = None
        expected = None
        assert CtsRepository.get_location_from_note(note) == expected

    def get_location_from_note_with_address_test(self):
        note = "#*Automation Engine*# DIS57079\n" \
               "Dispatch Management - Dispatch Requested\n\n" \
               "Please see the summary below.\n--\n" \
               "Dispatch Number: " \
               "[DIS57079|https://master.mettel-automation.net/dispatch_portal/dispatch/DIS57079] \n" \
               "Date of Dispatch: 2020-08-07\n" \
               "Time of Dispatch (Local): 10.00AM\n" \
               "Time Zone (Local): Eastern Time\n\n" \
               "Location Owner/Name: Marine Max\n" \
               "NO_ADDRESS: 750 S Federal Hwy , Pompano Beach, Florida, 33062\n" \
               "NO_CONTACT: MOD manager\n" \
               "Phone: (7) \n\n" \
               "Issues Experienced:\n" \
               "Please check their Wifi Network and other equipment as per the customer\n" \
               "Arrival Instructions: Please call HNOC and work with engineer\n" \
               "Materials Needed:\nButt set, extra CAT5 cable, punch down tool, laptop with TeamViewer, " \
               "multi-meter, crimper, DB9 console cable, Spare cable, Putty, wireless access\n\n" \
               "Requester\nName: Holmdel  NOC\nPhone: 8775206829\n" \
               "Email: holmdelnoc@mettel.net\n" \
               "Department: Holmdel Network Engineering"
        expected = None
        assert CtsRepository.get_location_from_note(note) == expected

    def get_sms_to_tech_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        expected_phone = "+12123595129"
        assert CtsRepository.get_sms_to_tech(updated_dispatch) == expected_phone

    def get_sms_to_tech_with_error_test(self, cts_dispatch_confirmed):
        updated_dispatch = copy.deepcopy(cts_dispatch_confirmed)
        updated_dispatch['Resource_Phone_Number__c'] = None
        assert CtsRepository.get_sms_to_tech(updated_dispatch) is None

    def is_dispatch_confirmed_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_not_confirmed):
        assert cts_dispatch_monitor._cts_repository.is_dispatch_confirmed(cts_dispatch_confirmed) is True
        assert cts_dispatch_monitor._cts_repository.is_dispatch_confirmed(cts_dispatch_not_confirmed) is False

    def is_tech_on_site_test(self, cts_dispatch_monitor, cts_dispatch_tech_on_site, cts_dispatch_tech_not_on_site):
        assert cts_dispatch_monitor._cts_repository.is_tech_on_site(cts_dispatch_tech_on_site) is True
        assert cts_dispatch_monitor._cts_repository.is_tech_on_site(cts_dispatch_tech_not_on_site) is False

    def is_cancelled_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, cts_dispatch_cancelled):
        assert cts_dispatch_monitor._cts_repository.is_dispatch_cancelled(cts_dispatch_confirmed) is False
        assert cts_dispatch_monitor._cts_repository.is_dispatch_cancelled(cts_dispatch_cancelled) is True

    def get_dispatches_splitted_by_status_test(self, cts_dispatch_monitor, cts_dispatch, cts_dispatch_confirmed,
                                               cts_dispatch_confirmed_2, cts_dispatch_tech_on_site,
                                               cts_bad_status_dispatch, cts_dispatch_cancelled):
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
            str(cts_dispatch_monitor._cts_repository.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL): [],
            str(cts_dispatch_monitor._cts_repository.DISPATCH_CANCELLED): []
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
    async def append_dispatch_cancelled_note_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                  append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_cancelled.get('Dispatch_Number')
        date_of_dispatch = cts_dispatch_cancelled.get('Local_Site_Time__c')
        date_time_of_dispatch_localized = iso8601.parse_date(date_of_dispatch, pytz.utc)
        # Get datetime formatted string
        DATETIME_FORMAT = '%b %d, %Y @ %I:%M %p UTC'
        date_of_dispatch = date_time_of_dispatch_localized.strftime(DATETIME_FORMAT)
        igz_dispatch_number = 'IGZ_0001'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\nDispatch Management - Dispatch Cancelled\n' \
                   f'Dispatch for {date_of_dispatch} has been cancelled.\n'

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note(
            dispatch_number, igz_dispatch_number, ticket_id, date_of_dispatch)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_dispatch_cancelled_note_error_test(self, cts_dispatch_monitor, cts_dispatch_cancelled,
                                                        append_note_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_cancelled.get('Dispatch_Number')
        date_of_dispatch = cts_dispatch_cancelled.get('Local_Site_Time__c')
        date_time_of_dispatch_localized = iso8601.parse_date(date_of_dispatch, pytz.utc)
        # Get datetime formatted string
        DATETIME_FORMAT = '%b %d, %Y @ %I:%M %p UTC'
        date_of_dispatch = date_time_of_dispatch_localized.strftime(DATETIME_FORMAT)
        igz_dispatch_number = 'IGZ_0001'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f'#*Automation Engine*# {igz_dispatch_number}\nDispatch Management - Dispatch Cancelled\n' \
                   f'Dispatch for {date_of_dispatch} has been cancelled.\n'
        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- Cancelled note not appended'

        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_dispatch_cancelled_note(
            dispatch_number, igz_dispatch_number, ticket_id, date_of_dispatch)

        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def send_confirmed_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
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
            dispatch_number, ticket_id, dispatch_datetime, sms_to, tech_name)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_not_valid_sms_to_phone_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed_no_contact):
        updated_dispatch = cts_dispatch_confirmed_no_contact.copy()
        ticket_id = '12345'
        dispatch_number = updated_dispatch.get('Name')
        tech_name = updated_dispatch.get('API_Resource_Name__c')
        sms_to = None
        dispatch_datetime = '2020-03-16 16:00:00 PDT'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_confirmed_sms(
            dispatch_number, ticket_id, dispatch_datetime, sms_to, tech_name)
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
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
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
            dispatch_number, ticket_id, dispatch_datetime, sms_to, tech_name)
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

    @pytest.mark.asyncio
    async def append_updated_tech_note_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f'#*Automation Engine*# {dispatch_number}\n' \
                   f'The Field Engineer assigned to this dispatch has changed.\n' \
                   f'Reference: {ticket_id}\n\n' \
                   f'Field Engineer\n{tech_name}\n{tech_phone}\n'
        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await cts_dispatch_monitor._cts_repository.append_updated_tech_note(
            dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_updated_tech_note_error_test(self, cts_dispatch_monitor, cts_dispatch_confirmed,
                                                  append_note_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        sms_to = '+1987654327'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        note_data = {
            'vendor': 'CTS',
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id,
            'tech_name': cts_dispatch_confirmed.get('API_Resource_Name__c'),
            'tech_phone': cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        }
        sms_note = f'#*Automation Engine*# {dispatch_number}\n' \
                   f'The Field Engineer assigned to this dispatch has changed.\n' \
                   f'Reference: {ticket_id}\n\n' \
                   f'Field Engineer\n{tech_name}\n{tech_phone}\n'

        send_error_sms_to_slack_response = f'An error occurred when appending an updated tech note ' \
                                           f'with bruin client. ' \
                                           f'Dispatch: {dispatch_number} - ' \
                                           f'Ticket_id: {ticket_id} - payload: {note_data}'

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.append_updated_tech_note(
            dispatch_number, ticket_id, cts_dispatch_confirmed)

        cts_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def send_updated_tech_sms_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = '+1987654327'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
        }

        sms_data = cts_get_updated_tech_sms(sms_data_payload)

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

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime,
            sms_to, tech_name)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_with_not_valid_sms_to_phone_test(self, cts_dispatch_monitor,
                                                                     cts_dispatch_confirmed_skipped_bad_phone):
        updated_dispatch = cts_dispatch_confirmed_skipped_bad_phone.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = None
        tech_name = updated_dispatch.get('API_Resource_Name__c')

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed_skipped_bad_phone, dispatch_datetime, sms_to, tech_name)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_updated_tech_sms_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
        }

        sms_data = cts_get_updated_tech_sms(sms_data_payload)

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
                                           f'An error occurred when sending Updated tech SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime,
            sms_to, tech_name)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = '+1987654327'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_updated_tech_sms_tech(sms_data_payload)

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

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is True

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_with_not_valid_sms_to_phone_test(self, cts_dispatch_monitor, cts_dispatch):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = None
        tech_name = cts_dispatch.get('API_Resource_Name__c')
        tech_phone = cts_dispatch.get('Resource_Phone_Number__c')
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name,
            'site': cts_dispatch.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch.get('Street__c')
        }

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, cts_dispatch, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_with_error_test(
            self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = cts_dispatch_confirmed.get('Name')
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_to = '+1987654327'
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        tech_phone = cts_dispatch_confirmed.get('Resource_Phone_Number__c')
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name,
            'site': cts_dispatch_confirmed.get('Lookup_Location_Owner__c'),
            'street': cts_dispatch_confirmed.get('Street__c')
        }

        sms_data = cts_get_updated_tech_sms_tech(sms_data_payload)

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
                                           f'An error occurred when sending Updated tech SMS tech ' \
                                           f'with notifier client. ' \
                                           f'payload: {sms_payload}'

        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await cts_dispatch_monitor._cts_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, cts_dispatch_confirmed, dispatch_datetime, sms_to)
        assert response is False

        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    def get_latest_tech_name_assigned_from_notes_test(self, cts_dispatch_monitor, cts_filtered_tickets_1,
                                                      cts_filtered_tickets_2):
        updated_notes = [cts_filtered_tickets_1[0]]
        expected = 'Berge, Keith'
        result = cts_dispatch_monitor._cts_repository.get_latest_tech_name_assigned_from_notes(
            updated_notes, cts_filtered_tickets_1, cts_dispatch_monitor.DISPATCH_UPDATED_TECH_WATERMARK
        )
        assert result == expected
        updated_notes = [cts_filtered_tickets_2[0]]
        expected = None
        result = cts_dispatch_monitor._cts_repository.get_latest_tech_name_assigned_from_notes(
            updated_notes, cts_filtered_tickets_2, cts_dispatch_monitor.DISPATCH_UPDATED_TECH_WATERMARK
        )
        assert result == expected
        expected = 'Berge, Keith'
        cts_filtered_tickets_1[4]['noteValue'] = cts_filtered_tickets_1[4]['noteValue'].replace('Field Engineer',
                                                                                                'The Field Engineer')
        updated_notes = [cts_filtered_tickets_1[4]]

        result = cts_dispatch_monitor._cts_repository.get_latest_tech_name_assigned_from_notes(
            updated_notes, cts_filtered_tickets_1, cts_dispatch_monitor.DISPATCH_UPDATED_TECH_WATERMARK
        )
        assert result == expected

    def filter_ticket_notes_by_dispatch_number_test(self, cts_dispatch_monitor, cts_ticket_notes_with_2_dispatches):
        igz_id_2 = 'IGZWtpGZCJopULhsiUhbWjUYf'
        expected = []
        for note in cts_ticket_notes_with_2_dispatches['ticketNotes']:
            if 'IGZWtpGZCJopULhsiUhbWjUYf' in note.get('noteValue'):
                expected.append(note)
        ticket_notes = cts_ticket_notes_with_2_dispatches.get('ticketNotes')
        result = cts_dispatch_monitor._cts_repository.filter_ticket_notes_by_dispatch_number(ticket_notes, igz_id_2)
        assert expected == result
        assert len(result) == 2

    def get_igz_dispatch_number_ok_test(self, cts_dispatch_monitor, cts_dispatch):
        dispatch_number = 'IGZ 1234'
        cts_dispatch['Description__c'] = (f"IGZ Dispatch Number: {dispatch_number}\n{cts_dispatch['Description__c']}")

        result = cts_dispatch_monitor._cts_repository.get_igz_dispatch_number(cts_dispatch)
        assert dispatch_number == result

    def get_igz_dispatch_number_not_id_test(self, cts_dispatch_monitor, cts_dispatch):
        dispatch_number = None

        result = cts_dispatch_monitor._cts_repository.get_igz_dispatch_number(cts_dispatch)
        assert dispatch_number == result

    @pytest.mark.asyncio
    async def append_note_ok_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Dispatch_Number')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 200
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        date_of_dispatch = cts_dispatch_confirmed.get('Local_Site_Time__c')
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            return_value=response_append_note_to_ticket_mock)
        result = await cts_dispatch_monitor._cts_repository.append_note(dispatch_number, ticket_id, date_of_dispatch,
                                                                        sms_note)
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note
        )
        assert result is True

    @pytest.mark.asyncio
    async def append_note_ko_test(self, cts_dispatch_monitor, cts_dispatch_confirmed):
        ticket_id = '12345'
        dispatch_number = cts_dispatch_confirmed.get('Dispatch_Number')
        igz_dispatch_number = 'IGZ_0001'
        sms_to = '+1987654327'
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        response_append_note_to_ticket_mock = {
            'body': '',
            'status': 400
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
        date_of_dispatch = cts_dispatch_confirmed.get('Local_Site_Time__c')
        err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                  f"- SMS {date_of_dispatch} hours note not appended"
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        cts_dispatch_monitor._cts_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            return_value=response_append_note_to_ticket_mock)
        result = await cts_dispatch_monitor._cts_repository.append_note(dispatch_number, ticket_id, date_of_dispatch,
                                                                        sms_note)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert result is False

    @pytest.mark.asyncio
    async def filter_send_sms_ok_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        dispatch_number = cts_dispatch_confirmed['Name']
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
        }
        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)
        result = await cts_dispatch_monitor._cts_repository.send_sms(dispatch_number, ticket_id, sms_to,
                                                                     dispatch_datetime,
                                                                     '', sms_payload)
        cts_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        assert result is True

    @pytest.mark.asyncio
    async def filter_send_sms_ko_test(self, cts_dispatch_monitor, cts_dispatch_confirmed, sms_success_response):
        dispatch_number = cts_dispatch_confirmed['Name']
        ticket_id = cts_dispatch_confirmed['Ext_Ref_Num__c']
        tech_name = cts_dispatch_confirmed.get('API_Resource_Name__c')
        sms_to = '+1987654327'
        dispatch_datetime = '2020-03-16 16:00:00 PDT'
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'tech_name': tech_name
        }
        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 400
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                  f'An error occurred when sending a tech {dispatch_datetime} hours SMS with notifier client. ' \
                  f'payload: {sms_payload}'
        cts_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        cts_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)
        result = await cts_dispatch_monitor._cts_repository.send_sms(dispatch_number, ticket_id, sms_to,
                                                                     dispatch_datetime,
                                                                     '', sms_payload)
        cts_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert result is False
