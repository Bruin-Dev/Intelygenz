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

from application.repositories.utils_repository import UtilsRepository
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
            res = lit_repository.get_dispatch_confirmed_date_time_localized(new_dispatch)
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

        response = lit_repository.get_dispatch_confirmed_date_time_localized(dispatch_confirmed)
        response_2 = lit_repository.get_dispatch_confirmed_date_time_localized(dispatch_confirmed_2)
        response_3 = lit_repository.get_dispatch_confirmed_date_time_localized(dispatch_confirmed_error)
        response_4 = lit_repository.get_dispatch_confirmed_date_time_localized(dispatch_confirmed_error_3)

        assert response == expected_response
        assert response_2 == expected_response_2
        assert response_3 is None
        assert response_4 is None
