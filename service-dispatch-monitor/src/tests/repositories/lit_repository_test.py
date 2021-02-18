import copy
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
import pytest

from asynctest import CoroutineMock
from pytz import timezone
from shortuuid import uuid

from application.repositories import lit_repository as lit_repository_module
from application.repositories import nats_error_response
from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_field_engineer_confirmed_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_x_hours_before_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_x_hours_before_sms
from application.templates.lit.sms.tech_on_site import lit_get_tech_on_site_sms

from application.repositories.utils_repository import UtilsRepository
from application.templates.lit.sms.updated_tech import lit_get_updated_tech_sms, lit_get_updated_tech_sms_tech
from config import testconfig
from application.repositories.lit_repository import LitRepository


uuid_ = uuid()
uuid_mock = patch.object(lit_repository_module, 'uuid', return_value=uuid_)


class TestLitRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        bruin_repository = Mock()

        lit_repository = LitRepository(logger, config, event_bus, notifications_repository, bruin_repository)

        assert lit_repository._event_bus is event_bus
        assert lit_repository._logger is logger
        assert lit_repository._config is config
        assert lit_repository._notifications_repository is notifications_repository
        assert lit_repository._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_all_dispatches_test(self, lit_repository, dispatch, dispatch_confirmed):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': {
                "Status": "Success",
                "Message": "Total Number of Dispatches: 2",
                "DispatchList": [
                    dispatch,
                    dispatch_confirmed
                ]
            },
            'status': 200,
        }
        lit_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        with uuid_mock:
            result = await lit_repository.get_all_dispatches()
        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_failing_test(self, lit_repository):

        request = {
            'request_id': uuid_,
            'body': {},
        }

        lit_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        lit_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await lit_repository.get_all_dispatches()

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=60)
        lit_repository._notifications_repository.send_slack_message.assert_awaited_once()
        lit_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_all_dispatches_with_rpc_request_returning_non_2xx_status_test(self, lit_repository):
        request = {
            'request_id': uuid_,
            'body': {},
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from LIT',
            'status': 500,
        }

        lit_repository._event_bus.rpc_request = CoroutineMock(return_value=response)
        lit_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await lit_repository.get_all_dispatches()

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=60)
        lit_repository._notifications_repository.send_slack_message.assert_awaited_once()
        lit_repository._logger.error.assert_called_once()
        assert result == response

    def get_sms_to_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = "Test Client on site +1 (212) 359-5129"
        expected_phone = "+12123595129"
        assert LitRepository.get_sms_to(updated_dispatch) == expected_phone

    def get_sms_to_with_error_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = None
        assert LitRepository.get_sms_to(updated_dispatch) is None

    def get_sms_to_with_error_number_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = "no valid Number"
        assert LitRepository.get_sms_to(updated_dispatch) is None

    def get_sms_to_tech_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Tech_Mobile_Number'] = "+1 (212) 359-5129"
        expected_phone = "+12123595129"
        assert LitRepository.get_sms_to_tech(updated_dispatch) == expected_phone

    def get_sms_to_tech_with_error_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Tech_Mobile_Number'] = None
        assert LitRepository.get_sms_to_tech(updated_dispatch) is None

    def get_sms_to_tech_with_error_number_test(self, dispatch):
        updated_dispatch = copy.deepcopy(dispatch)
        updated_dispatch['Tech_Mobile_Number'] = "no valid Number"
        assert LitRepository.get_sms_to_tech(updated_dispatch) is None

    def get_dispatch_confirmed_date_time_localized_regex_test(self, lit_repository, dispatch_confirmed):
        dates = [
            {'date': '4-6pm', 'am_pm': 'PM', 'final': '4:00'},
            {'date': '4pm-6pm', 'am_pm': 'PM', 'final': '4:00'},
            {'date': '12pm', 'am_pm': 'PM', 'final': '12:00'},
            {'date': '12:00PM', 'am_pm': 'PM', 'final': '12:00'},
            {'date': '9:00 AM', 'am_pm': 'AM', 'final': '9:00'},
            {'date': '10 am', 'am_pm': 'AM', 'final': '10:00'},
            {'date': '10am ET', 'am_pm': 'AM', 'final': '10:00'},
            {'date': '10a-12p ET', 'am_pm': 'AM', 'final': '10:00'},
            {'date': '11a-1p PT', 'am_pm': 'AM', 'final': '11:00'},
            {'date': '2-4pm ET', 'am_pm': 'PM', 'final': '2:00'},
            {'date': '12-2PM CT', 'am_pm': 'PM', 'final': '12:00'},
            {'date': '11am CT', 'am_pm': 'AM', 'final': '11:00'},
            {'date': '12:00', 'am_pm': None, 'final': None},
            {'date': '3:30pm ET', 'am_pm': 'PM', 'final': '3:30'},
            {'date': '12::00PM', 'am_pm': 'PM', 'final': '12:00'},
            {'date': '8am-1p PT', 'am_pm': 'AM', 'final': '8:00'},
            {'date': '7.00PM', 'am_pm': 'PM', 'final': '7:00'},
            {'date': '1.30AM', 'am_pm': 'AM', 'final': '1:30'},
            {'date': '8 AM CT', 'am_pm': 'AM', 'final': '8:00'},
            {'date': None, 'am_pm': None, 'final': None},
            {'date': '3:30a ET', 'am_pm': 'AM', 'final': '3:30'},
            {'date': '3:30p ET', 'am_pm': 'PM', 'final': '3:30'},
            {'date': '3:30pm ET', 'am_pm': 'PM', 'final': '3:30'},
            {'date': '3:30pm ET', 'am_pm': 'PM', 'final': '3:30', 'tz': 'BAD'}
        ]
        responses = []
        expected_responses = []
        for test_date in dates:
            new_dispatch = copy.deepcopy(dispatch_confirmed)

            dispatch_number = new_dispatch.get('Dispatch_Number')
            ticket_id = new_dispatch.get('MetTel_Bruin_TicketID')
            date_of_dispatch = new_dispatch.get('Date_of_Dispatch', None)

            new_dispatch['Hard_Time_of_Dispatch_Local'] = test_date['date']
            if 'tz' in test_date:
                new_dispatch['Hard_Time_of_Dispatch_Time_Zone_Local'] = test_date['tz']

            final_time_of_dispatch = test_date['final']
            am_pm = test_date['am_pm']

            expected_response = None
            new_dispatch['Hard_Time_of_Dispatch_Local'] = test_date['date']
            if am_pm is not None:
                final_timezone = timezone(f'US/Pacific')
                final_datetime = datetime.strptime(f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}',
                                                   lit_repository.DATETIME_TZ_FORMAT)
                return_datetime_localized = final_timezone.localize(final_datetime)
            res = lit_repository.get_dispatch_confirmed_date_time_localized(new_dispatch, dispatch_number, ticket_id)
            if res is None:
                responses.append(res)
                expected_responses.append(None)
            else:
                responses.append(res)
                expected_response = {
                    'datetime_localized': return_datetime_localized,
                    'timezone': final_timezone,
                    'datetime_formatted_str': return_datetime_localized.strftime(
                        lit_repository.DATETIME_FORMAT.format(time_zone_of_dispatch='Pacific'))
                }
                expected_responses.append(expected_response)
            assert res == expected_response

        assert responses == expected_responses

    def get_dispatch_confirmed_date_time_localized_test(self, lit_repository, dispatch_confirmed, dispatch_confirmed_2,
                                                        dispatch_confirmed_error, dispatch_confirmed_error_2):
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        ticket_id = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        date_of_dispatch = dispatch_confirmed.get('Date_of_Dispatch', None)
        final_time_of_dispatch = '4:00'
        am_pm = 'PM'
        final_timezone = timezone(f'US/Pacific')
        final_datetime = datetime.strptime(f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}', "%Y-%m-%d %I:%M%p")
        return_datetime_localized = final_timezone.localize(final_datetime)

        expected_response = {
            'datetime_localized': return_datetime_localized,
            'timezone': final_timezone,
            'datetime_formatted_str': 'Mar 16, 2020 @ 04:00 PM Pacific'
        }

        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')
        date_of_dispatch_2 = dispatch_confirmed_2.get('Date_of_Dispatch')
        final_time_of_dispatch_2 = '10:30'
        am_pm_2 = 'AM'
        final_timezone_2 = timezone(f'US/Eastern')
        final_datetime_2 = datetime.strptime(f'{date_of_dispatch_2} {final_time_of_dispatch_2}{am_pm_2}',
                                             lit_repository.DATETIME_TZ_FORMAT)
        return_datetime_localized_2 = final_timezone_2.localize(final_datetime_2)

        expected_response_2 = {
            'datetime_localized': return_datetime_localized_2,
            'timezone': final_timezone_2,
            'datetime_formatted_str': 'Mar 16, 2020 @ 10:30 AM Eastern'
        }

        response = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed, dispatch_number, ticket_id)
        response_2 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_2, dispatch_number_2, ticket_id_2)
        response_3 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_error, dispatch_number_2, ticket_id_2)
        response_4 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_error_2, dispatch_number_2, ticket_id_2)

        assert response == expected_response
        assert response_2 == expected_response_2
        assert response_3 is None
        assert response_4 is None

    def get_dispatch_confirmed_date_time_localized_error_timezone_test(
            self, lit_repository, dispatch_confirmed, dispatch_confirmed_2, dispatch_confirmed_error,
            dispatch_confirmed_error_3):
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        ticket_id = dispatch_confirmed.get('MetTel_Bruin_TicketID')
        date_of_dispatch = dispatch_confirmed.get('Date_of_Dispatch', None)
        final_time_of_dispatch = '4:00'
        am_pm = 'PM'
        final_timezone = timezone(f'US/Pacific')
        final_datetime = datetime.strptime(f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}', "%Y-%m-%d %I:%M%p")
        return_datetime_localized = final_timezone.localize(final_datetime)

        expected_response = {
            'datetime_localized': return_datetime_localized,
            'timezone': final_timezone,
            'datetime_formatted_str': 'Mar 16, 2020 @ 04:00 PM Pacific'
        }

        dispatch_number_2 = dispatch_confirmed_2.get('Dispatch_Number')
        ticket_id_2 = dispatch_confirmed_2.get('MetTel_Bruin_TicketID')
        date_of_dispatch_2 = dispatch_confirmed_2.get('Date_of_Dispatch')
        final_time_of_dispatch_2 = '10:30'
        am_pm_2 = 'AM'
        final_timezone_2 = timezone(f'US/Eastern')
        final_datetime_2 = datetime.strptime(f'{date_of_dispatch_2} {final_time_of_dispatch_2}{am_pm_2}',
                                             lit_repository.DATETIME_TZ_FORMAT)
        return_datetime_localized_2 = final_timezone_2.localize(final_datetime_2)

        expected_response_2 = {
            'datetime_localized': return_datetime_localized_2,
            'timezone': final_timezone_2,
            'datetime_formatted_str': 'Mar 16, 2020 @ 10:30 AM Eastern'
        }

        response = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed, dispatch_number, ticket_id)
        response_2 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_2, dispatch_number_2, ticket_id_2)
        response_3 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_error, dispatch_number_2, ticket_id_2)
        response_4 = lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_confirmed_error_3, dispatch_number_2, ticket_id_2)

        assert response == expected_response
        assert response_2 == expected_response_2
        assert response_3 is None
        assert response_4 is None

    def get_dispatches_splitted_by_status_test(self, lit_dispatch_monitor, dispatch, dispatch_confirmed,
                                               dispatch_confirmed_2, dispatch_tech_on_site, dispatch_completed,
                                               dispatch_cancelled,
                                               bad_status_dispatch):
        dispatches = [
            dispatch, dispatch_confirmed, dispatch_confirmed_2,
            dispatch_tech_on_site, dispatch_completed, dispatch_cancelled, bad_status_dispatch
        ]
        expected_dispatches_splitted = {
            str(lit_dispatch_monitor._lit_repository.DISPATCH_REQUESTED): [dispatch],
            str(lit_dispatch_monitor._lit_repository.DISPATCH_CONFIRMED): [dispatch_confirmed, dispatch_confirmed_2],
            str(lit_dispatch_monitor._lit_repository.DISPATCH_FIELD_ENGINEER_ON_SITE): [dispatch_tech_on_site],
            str(lit_dispatch_monitor._lit_repository.DISPATCH_REPAIR_COMPLETED): [dispatch_completed],
            str(lit_dispatch_monitor._lit_repository.DISPATCH_CANCELLED): [dispatch_cancelled]
        }
        result = lit_dispatch_monitor._lit_repository.get_dispatches_splitted_by_status(dispatches)
        assert result == expected_dispatches_splitted

    def is_dispatch_confirmed_test(self, lit_dispatch_monitor, dispatch_confirmed, dispatch_not_confirmed):
        assert lit_dispatch_monitor._lit_repository.is_dispatch_confirmed(dispatch_confirmed) is True
        assert lit_dispatch_monitor._lit_repository.is_dispatch_confirmed(dispatch_not_confirmed) is False

    def is_tech_on_site_test(self, lit_dispatch_monitor, dispatch_tech_on_site, dispatch_tech_not_on_site):
        assert lit_dispatch_monitor._lit_repository.is_tech_on_site(dispatch_tech_on_site) is True
        assert lit_dispatch_monitor._lit_repository.is_tech_on_site(dispatch_tech_not_on_site) is False

    def is_repair_completed_test(self, lit_dispatch_monitor, dispatch_completed, dispatch_not_completed):
        assert lit_dispatch_monitor._lit_repository.is_repair_completed(dispatch_completed) is True
        assert lit_dispatch_monitor._lit_repository.is_repair_completed(dispatch_not_completed) is False

    def is_cancelled_test(self, lit_dispatch_monitor, dispatch_confirmed, dispatch_cancelled):
        assert lit_dispatch_monitor._lit_repository.is_dispatch_cancelled(dispatch_confirmed) is False
        assert lit_dispatch_monitor._lit_repository.is_dispatch_cancelled(dispatch_cancelled) is True

    @pytest.mark.asyncio
    async def send_confirmed_sms_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_with_error_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

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
                                           f'An error occurred when sending Confirmed SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_confirmed_field_engineer_sms_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                     sms_success_response):
        ticket_id = '3544800'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'tech_name': tech_name
        }

        sms_data = lit_get_dispatch_field_engineer_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_field_engineer_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], tech_name, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_field_engineer_sms_invalid_sms_to_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                                    sms_success_response):
        ticket_id = '3544800'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = None

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_field_engineer_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], tech_name, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_field_engineer_sms_error_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                           sms_success_response):
        ticket_id = '3544800'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'tech_name': tech_name
        }

        sms_data = lit_get_dispatch_field_engineer_confirmed_sms(sms_data_payload)

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
                                           f'An error occurred when sending Confirmed Field Engineer ' \
                                           f'SMS with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        response = await lit_dispatch_monitor._lit_repository.send_confirmed_field_engineer_sms(
            dispatch_number, ticket_id, datetime_return_1['datetime_formatted_str'], tech_name, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'site': dispatch_confirmed.get('Job_Site'),
            'street': dispatch_confirmed.get('Job_Site_Street')
        }

        sms_data = lit_get_dispatch_confirmed_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, dispatch, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_confirmed_sms_tech_with_error_test(
            self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'site': dispatch_confirmed.get('Job_Site'),
            'street': dispatch_confirmed.get('Job_Site_Street')
        }

        sms_data = lit_get_dispatch_confirmed_sms_tech(sms_data_payload)

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
                                           f'with notifier client. ' \
                                           f'payload: {sms_payload}'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_confirmed_sms_tech(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_sms_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_x_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        current_hour = '12'

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_sms(
            dispatch_number, ticket_id, sms_to, current_hour, sms_payload)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_sms_with_error_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_x_hours_before_sms(sms_data_payload)

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

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        current_hour = '12'

        response = await lit_dispatch_monitor._lit_repository.send_sms(
            dispatch_number, ticket_id, sms_to, current_hour, sms_payload)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_tech_on_site_sms(dispatch_number, ticket_id,
                                                                                    dispatch, sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_tech_on_site_sms(
            dispatch_number, ticket_id, updated_dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_tech_on_site_sms_with_error_test(self, lit_dispatch_monitor, dispatch, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        # sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        # sms_to = LitRepository.get_sms_to(dispatch)
        sms_to = '+1987654327'
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

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

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_tech_on_site_sms(
            dispatch_number, ticket_id, dispatch, sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'tech_name': tech_name
        }

        sms_data = lit_get_updated_tech_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'],
            sms_to, tech_name)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None
        tech_name = updated_dispatch.get('Tech_First_Name')

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, dispatch, datetime_return_1['datetime_formatted_str'], sms_to, tech_name)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_updated_tech_sms_with_error_test(
            self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'tech_name': tech_name
        }

        sms_data = lit_get_updated_tech_sms(sms_data_payload)

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

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'],
            sms_to, tech_name)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_test(self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'tech_name': tech_name,
            'site': dispatch_confirmed.get('Job_Site'),
            'street': dispatch_confirmed.get('Job_Site_Street')
        }

        sms_data = lit_get_updated_tech_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }

        send_sms_response = {
            'request_id': uuid_,
            'body': sms_success_response,
            'status': 200
        }

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(return_value=send_sms_response)

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is True

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_with_not_valid_sms_to_phone_test(self, lit_dispatch_monitor, dispatch):
        updated_dispatch = dispatch.copy()
        ticket_id = '3544800'
        dispatch_number = updated_dispatch.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        updated_dispatch['Job_Site_Contact_Name_and_Phone_Number'] = 'NOT VALID PHONE'
        sms_to = None
        tech_name = updated_dispatch.get('Tech_First_Name')

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, dispatch, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_not_awaited()

    @pytest.mark.asyncio
    async def send_updated_tech_sms_tech_with_error_test(
            self, lit_dispatch_monitor, dispatch_confirmed, sms_success_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        tz_1 = timezone(f'US/Pacific')
        time_1 = tz_1.localize(datetime.strptime('2020-03-16 4:00PM', '%Y-%m-%d %I:%M%p'))
        datetime_return_1 = {
            'datetime_localized': time_1,
            'timezone': tz_1,
            'datetime_formatted_str': time_1.strftime(UtilsRepository.DATETIME_FORMAT)
        }
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        sms_data_payload = {
            'date_of_dispatch': datetime_return_1['datetime_formatted_str'],
            'phone_number': sms_to,
            'tech_name': tech_name,
            'site': dispatch_confirmed.get('Job_Site'),
            'street': dispatch_confirmed.get('Job_Site_Street')
        }

        sms_data = lit_get_updated_tech_sms_tech(sms_data_payload)

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

        lit_dispatch_monitor._notifications_repository.send_sms = CoroutineMock(side_effect=[send_sms_response])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.send_updated_tech_sms_tech(
            dispatch_number, ticket_id, dispatch_confirmed, datetime_return_1['datetime_formatted_str'], sms_to)
        assert response is False

        lit_dispatch_monitor._notifications_repository.send_sms.assert_awaited_once_with(sms_payload)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)

    @pytest.mark.asyncio
    async def append_confirmed_note_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Dispatch Confirmed\n" \
                   'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        note_data = {
            'vendor': 'LIT',
            'dispatch_number': dispatch_number,
            'date_of_dispatch': dispatch_confirmed.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch_confirmed.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch_confirmed.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Dispatch Confirmed\n" \
                   'Dispatch scheduled for 2020-03-16 @ 4PM-6PM Pacific Time\n'

        send_error_sms_to_slack_response = f'An error occurred when appending a confirmed note with bruin client. ' \
                                           f'Dispatch: {dispatch_number} - ' \
                                           f'Ticket_id: {ticket_id} - payload: {note_data}'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_confirmed_field_engineer_note_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                        append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        tech_phone = dispatch_confirmed.get('Tech_Mobile_Number')
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        note_contents = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Field Engineer Confirmed\n\n" \
                        f"Field Engineer\n{tech_name}\n{tech_phone}\n"

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_field_engineer_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, note_contents)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_field_engineer_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                              append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        tech_name = dispatch_confirmed.get('Tech_First_Name')
        tech_phone = dispatch_confirmed.get('Tech_Mobile_Number')
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        note_contents = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Field Engineer Confirmed\n\n" \
                        f"Field Engineer\n{tech_name}\n{tech_phone}\n"
        slack_error_message = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{note_contents}` " \
                              f"- Field Engineer Confirmed note not appended"
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()
        response = await lit_dispatch_monitor._lit_repository.append_confirmed_field_engineer_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, note_contents)
        assert response is False
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(slack_error_message)

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch confirmation SMS sent to +1987654327\n"
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_sms_note(
            dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch confirmation SMS sent to +1987654327\n"

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS Confirmed note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_sms_note(
            dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_confirmed_sms_tech_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch confirmation SMS tech sent to +1987654327\n"
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note(
            dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_confirmed_sms_tech_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch confirmation SMS tech sent to +1987654327\n"

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- Tech SMS Confirmed note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.append_confirmed_sms_tech_note(
            dispatch_number, ticket_id, sms_to)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_note_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch 12h prior reminder SMS sent to +1987654327\n"
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        current_hour = '12'

        response = await lit_dispatch_monitor._lit_repository.append_note(
            dispatch_number, ticket_id, current_hour, sms_note)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_note_error_test(self, lit_dispatch_monitor, dispatch, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch 12h prior reminder SMS sent to +1987654327\n"

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS 12 hours note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        current_hour = '12'

        response = await lit_dispatch_monitor._lit_repository.append_note(
            dispatch_number, ticket_id, current_hour, sms_note)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Field Engineer On Site\n" \
                   'SMS notification sent to +1987654327\n\nThe field engineer, Joe Malone has arrived.\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note(
            dispatch_number, ticket_id, sms_to, dispatch_confirmed.get('Tech_First_Name'))

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_tech_on_site_sms_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed,
                                                      append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Field Engineer On Site\n" \
                   'SMS notification sent to +1987654327\n\nThe field engineer, Joe Malone has arrived.\n'

        send_error_sms_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` ' \
                                           f'- SMS tech on site note not appended'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.append_tech_on_site_sms_note(
            dispatch_number, ticket_id, sms_to, dispatch_confirmed.get('Tech_First_Name'))

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_dispatch_cancelled_note_test(self, lit_dispatch_monitor, dispatch_cancelled,
                                                  append_note_response):
        ticket_id = '12345'
        dispatch_number = dispatch_cancelled.get('Dispatch_Number')
        date_of_dispatch_tz = lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_cancelled, dispatch_number, ticket_id)
        date_of_dispatch = date_of_dispatch_tz['datetime_formatted_str']

        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Dispatch Cancelled\n" \
                   f'Dispatch for {date_of_dispatch} has been cancelled.\n'

        lit_dispatch_monitor._lit_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_dispatch_cancelled_note(
            dispatch_number, ticket_id, date_of_dispatch)

        lit_dispatch_monitor._lit_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_dispatch_cancelled_note_error_test(self, lit_dispatch_monitor, dispatch_cancelled,
                                                        append_note_response):
        ticket_id = '12345'
        dispatch_number = dispatch_cancelled.get('Dispatch_Number')
        date_of_dispatch_tz = lit_dispatch_monitor._lit_repository.get_dispatch_confirmed_date_time_localized(
            dispatch_cancelled, dispatch_number, ticket_id)
        date_of_dispatch = date_of_dispatch_tz['datetime_formatted_str']
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        cancel_note = f"#*MetTel's IPA*# {dispatch_number}\nDispatch Management - Dispatch Cancelled\n" \
                      f'Dispatch for {date_of_dispatch} has been cancelled.\n'
        send_error_cancel_to_slack_response = f'Dispatch: {dispatch_number} Ticket_id: {ticket_id} ' \
                                              f'Note: `{cancel_note}` ' \
                                              f'- Cancelled note not appended'

        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        lit_dispatch_monitor._lit_repository._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_dispatch_cancelled_note(
            dispatch_number, ticket_id, date_of_dispatch)

        lit_dispatch_monitor._lit_repository._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, cancel_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_cancel_to_slack_response)
        assert response is False

    @pytest.mark.asyncio
    async def append_updated_tech_note_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 200
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\n" \
                   f'The Field Engineer assigned to this dispatch has changed.\n' \
                   f'Reference: {ticket_id}\n\n' \
                   'Field Engineer\nJoe Malone\n+12123595129\n'
        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])

        response = await lit_dispatch_monitor._lit_repository.append_updated_tech_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        assert response is True

    @pytest.mark.asyncio
    async def append_updated_tech_note_error_test(self, lit_dispatch_monitor, dispatch_confirmed, append_note_response):
        ticket_id = '3544800'
        dispatch_number = dispatch_confirmed.get('Dispatch_Number')
        sms_to = '+1987654327'
        response_append_note_1 = {
            'request_id': uuid_,
            'body': append_note_response,
            'status': 400
        }
        note_data = {
            'vendor': 'LIT',
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id,
            'tech_name': dispatch_confirmed.get('Tech_First_Name'),
            'tech_phone': dispatch_confirmed.get('Tech_Mobile_Number')
        }
        sms_note = f"#*MetTel's IPA*# {dispatch_number}\n" \
                   f'The Field Engineer assigned to this dispatch has changed.\n' \
                   f'Reference: {ticket_id}\n\n' \
                   'Field Engineer\nJoe Malone\n+12123595129\n'

        send_error_sms_to_slack_response = f'An error occurred when appending an updated tech note ' \
                                           f'with bruin client. ' \
                                           f'Dispatch: {dispatch_number} - ' \
                                           f'Ticket_id: {ticket_id} - payload: {note_data}'

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket = CoroutineMock(
            side_effect=[response_append_note_1])
        lit_dispatch_monitor._notifications_repository.send_slack_message = CoroutineMock()

        response = await lit_dispatch_monitor._lit_repository.append_updated_tech_note(
            dispatch_number, ticket_id, dispatch_confirmed)

        lit_dispatch_monitor._bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, sms_note)
        lit_dispatch_monitor._notifications_repository.send_slack_message.assert_awaited_once_with(
            send_error_sms_to_slack_response)
        assert response is False
