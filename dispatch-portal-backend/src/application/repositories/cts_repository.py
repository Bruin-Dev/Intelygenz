import re
from datetime import datetime

import pytz
from pytz import timezone


class CtsRepository:
    def __init__(self, logger, config, event_bus, notifications_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self.DATETIME_FORMAT = '%b %d, %Y @ %I:%M %p UTC'

    def _find_field_in_dispatch_description(self, dispatch, field_name):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        field = None
        for line in description_lines:
            if line and len(line) > 0 and field_name in line:
                field = ''.join(ch for ch in line)
                break
        if field is None or field.strip() == '':
            return None
        return field.strip().replace(f'{field_name}: ', '')

    def get_onsite_time_needed(self, dispatch):
        onsite_time_needed = self._find_field_in_dispatch_description(dispatch, 'Onsite Time Needed')

        # onsite time needed format: '2020-06-21 4.00PM', check the '.' and not ':'
        regex_result = re.search(" (.*?)\\.", onsite_time_needed)
        if regex_result:
            current_hour = regex_result.group(1)
        else:
            return None

        if 'PM' in onsite_time_needed:
            if int(current_hour) < 12:
                new_hour = str(int(current_hour) + 12)
                onsite_time_needed = onsite_time_needed.replace(f"{current_hour}.", f"{new_hour}.")
            onsite_time_needed = onsite_time_needed.replace('.', ':').replace('PM', '')
        elif 'AM' in onsite_time_needed:
            if int(current_hour) == 12:
                onsite_time_needed = onsite_time_needed.replace(f"{current_hour}.", "00.")
            onsite_time_needed = onsite_time_needed.replace('.', ':').replace('AM', '')

        time_stamp_string = f'{onsite_time_needed}:00.00'
        final_timestamp = datetime.strptime(time_stamp_string, '%Y-%m-%d %H:%M:%S.%f')
        return final_timestamp

    def get_onsite_timezone(self, dispatch):
        onsite_timezone = self._find_field_in_dispatch_description(dispatch, 'Onsite Timezone')
        time_zone_of_dispatch = onsite_timezone.replace('Time', '').replace(' ', '')
        final_timezone = timezone(f'US/{time_zone_of_dispatch}')
        return final_timezone

    def get_dispatch_confirmed_date_time_localized(self, dispatch):
        # https://intelygenz.atlassian.net/browse/MET-559

        onsite_time_needed = self.get_onsite_time_needed(dispatch)
        onsite_timezone = self.get_onsite_timezone(dispatch)

        if onsite_time_needed is None or onsite_timezone is None:
            return None

        self._logger.info(f"- Time and timezone from description: {onsite_time_needed} - {onsite_timezone}")

        self._logger.info(f"- Converting: {onsite_time_needed} to UTC")

        date_time_of_dispatch_localized = onsite_timezone.localize(onsite_time_needed)
        date_time_of_dispatch_localized = date_time_of_dispatch_localized.astimezone(pytz.utc)
        datetime_formatted_str = date_time_of_dispatch_localized.strftime(self.DATETIME_FORMAT)

        response = {
            'date_time_of_dispatch_localized': date_time_of_dispatch_localized,
            'timezone': onsite_timezone,
            'datetime_formatted_str': datetime_formatted_str
        }

        self._logger.info(f"- Converted: {response}")

        return response
