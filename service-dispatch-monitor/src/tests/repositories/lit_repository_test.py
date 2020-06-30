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
from application.repositories.lit_repository import LitRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(lit_repository_module, 'uuid', return_value=uuid_)


class TestLitRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        lit_repository = LitRepository(logger, config, event_bus, notifications_repository)

        assert lit_repository._event_bus is event_bus
        assert lit_repository._logger is logger
        assert lit_repository._config is config
        assert lit_repository._notifications_repository is notifications_repository

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
        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
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

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
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

        lit_repository._event_bus.rpc_request.assert_awaited_once_with("lit.dispatch.get", request, timeout=30)
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
                    'timezone': final_timezone
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
            'timezone': final_timezone
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
            'timezone': final_timezone_2
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
            'timezone': final_timezone
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
            'timezone': final_timezone_2
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
