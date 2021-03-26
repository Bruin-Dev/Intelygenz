from datetime import datetime
import pytz
from pytz import timezone
from unittest.mock import Mock

from config import testconfig
from application.repositories.cts_repository import CtsRepository


class TestCtsRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        cts_repository = CtsRepository(logger, config, event_bus, notifications_repository)

        assert cts_repository._event_bus is event_bus
        assert cts_repository._logger is logger
        assert cts_repository._config is config
        assert cts_repository._notifications_repository is notifications_repository

    def find_field_in_dispatch_description_test(self, cts_repository, cts_dispatch_confirmed):
        expected = '2020-06-21 4.00PM'
        expected_2 = 'Pacific Time'
        assert cts_repository._find_field_in_dispatch_description(cts_dispatch_confirmed,
                                                                  'Onsite Time Needed') == expected
        assert cts_repository._find_field_in_dispatch_description(cts_dispatch_confirmed,
                                                                  'Onsite Timezone') == expected_2

    def find_field_in_dispatch_description_none_description_test(self, cts_repository,
                                                                 cts_dispatch_confirmed_none_description):
        expected = None
        expected_2 = None
        assert cts_repository._find_field_in_dispatch_description(cts_dispatch_confirmed_none_description,
                                                                  'Onsite Time Needed') == expected
        assert cts_repository._find_field_in_dispatch_description(cts_dispatch_confirmed_none_description,
                                                                  'Onsite Timezone') == expected_2

    def get_requester_info_test(self, cts_repository, cts_dispatch_confirmed):
        requester_info = cts_repository.get_requester_info(cts_dispatch_confirmed)
        assert requester_info['requester_name'] == 'Karen Doe'
        assert requester_info['requester_phone'] == '+1 666 666 6666'
        assert requester_info['requester_email'] == 'karen.doe@mettel.net'

    def get_onsite_time_needed_test(self, cts_repository, cts_dispatch_confirmed,
                                    cts_dispatch_confirmed_none_description,
                                    cts_dispatch_confirmed_bad_date,
                                    cts_dispatch_confirmed_empty_address,
                                    cts_dispatch_confirmed_2, cts_dispatch_confirmed_3):
        onsite_time_needed = '2020-06-21 16:00'
        time_stamp_string = f'{onsite_time_needed}:00.00'
        expected = datetime.strptime(time_stamp_string, '%Y-%m-%d %H:%M:%S.%f')

        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed) == expected
        expected_2 = None
        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed_none_description) == expected_2
        expected_3 = None
        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed_bad_date) == expected_3
        expected_4 = None
        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed_empty_address) == expected_4

        onsite_time_needed_2 = '2020-06-21 4:00'
        time_stamp_string_2 = f'{onsite_time_needed_2}:00.00'
        expected_5 = datetime.strptime(time_stamp_string_2, '%Y-%m-%d %H:%M:%S.%f')
        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed_2) == expected_5

        onsite_time_needed_3 = '2020-06-21 0:00'
        time_stamp_string_3 = f'{onsite_time_needed_3}:00.00'
        expected_6 = datetime.strptime(time_stamp_string_3, '%Y-%m-%d %H:%M:%S.%f')
        assert cts_repository.get_onsite_time_needed(cts_dispatch_confirmed_3) == expected_6

    def get_onsite_timezone_test(self, cts_repository, cts_dispatch_confirmed,
                                 cts_dispatch_confirmed_none_description,
                                 cts_dispatch_confirmed_bad_date):
        from pytz import timezone
        expected = timezone(f'US/Pacific')

        assert cts_repository.get_onsite_timezone(cts_dispatch_confirmed) == expected
        expected_2 = None
        assert cts_repository.get_onsite_timezone(cts_dispatch_confirmed_none_description) == expected_2
        expected_3 = None
        assert cts_repository.get_onsite_timezone(cts_dispatch_confirmed_bad_date) == expected_3

    def get_dispatch_confirmed_date_time_localized_test(self, cts_repository, cts_dispatch_confirmed,
                                                        cts_dispatch_confirmed_none_description,
                                                        cts_dispatch_confirmed_bad_date):
        tz = timezone(f'US/Pacific')
        onsite_time_needed = '2020-06-21 16:00'
        time_stamp_string = f'{onsite_time_needed}:00.00'
        date_time_of_dispatch_localized = datetime.strptime(time_stamp_string, '%Y-%m-%d %H:%M:%S.%f')
        datetime_formatted_str = 'Jun 21, 2020 @ 04:00 PM US/Pacific'
        date_time_of_dispatch_localized = tz.localize(date_time_of_dispatch_localized)
        date_time_of_dispatch_localized = date_time_of_dispatch_localized.astimezone(pytz.utc)

        expected = {
            'date_time_of_dispatch_localized': date_time_of_dispatch_localized,
            'timezone': tz,
            'datetime_formatted_str': datetime_formatted_str
        }
        response = cts_repository.get_dispatch_confirmed_date_time_localized(cts_dispatch_confirmed)
        assert response == expected
        expected_2 = None
        response_2 = cts_repository.get_dispatch_confirmed_date_time_localized(cts_dispatch_confirmed_none_description)
        assert response_2 == expected_2
        expected_3 = None
        response_3 = cts_repository.get_dispatch_confirmed_date_time_localized(cts_dispatch_confirmed_bad_date)
        assert response_3 == expected_3
