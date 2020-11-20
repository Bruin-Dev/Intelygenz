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
        self.DISPATCH_CONFIRMED = 'Scheduled'

    def _find_field_in_dispatch_description(self, dispatch, field_name):
        description = '' if not dispatch.get('Description__c') else dispatch.get('Description__c')
        description_lines = description.splitlines()
        field = None
        for line in description_lines:
            if line and len(line) > 0 and field_name in line:
                field = ''.join(ch for ch in line)
                break
        if field is None or field.strip() == '':
            return None
        return field.strip().replace(f'{field_name}: ', '')

    def get_requester_info(self, dispatch):
        requester_info = {}

        requester_info['requester_name'] = self._find_field_in_dispatch_description(dispatch, 'Name')
        requester_info['requester_phone'] = self._find_field_in_dispatch_description(dispatch, 'Phone')
        requester_info['requester_email'] = self._find_field_in_dispatch_description(dispatch, 'Email')

        return requester_info

    def get_onsite_time_needed(self, dispatch):
        onsite_time_needed = self._find_field_in_dispatch_description(dispatch, 'Onsite Time Needed')
        try:
            onsite_time_needed_time_stamp = datetime.strptime(onsite_time_needed, "%Y-%m-%d %I.%M%p")
            refactored_timestamp = datetime.strftime(onsite_time_needed_time_stamp, '%Y-%m-%d %H:%M:%S.%f')
            final_timestamp = datetime.strptime(refactored_timestamp, '%Y-%m-%d %H:%M:%S.%f')
            return final_timestamp
        except Exception as ex:
            dispatch_number = dispatch.get('Name', None) if dispatch else 'no dispatch number'
            self._logger.info(f"Error: getting get_onsite_time_needed for dispatch: {dispatch_number} -> {ex}")
            return None

    def get_onsite_timezone(self, dispatch):
        onsite_timezone = self._find_field_in_dispatch_description(dispatch, 'Onsite Timezone')
        if not onsite_timezone:
            return None
        time_zone_of_dispatch = onsite_timezone.replace('Time', '').replace(' ', '')
        final_timezone = timezone(f'US/{time_zone_of_dispatch}')
        return final_timezone

    def get_dispatch_confirmed_date_time_localized(self, dispatch):
        # https://intelygenz.atlassian.net/browse/MET-559
        dispatch_number = dispatch.get('Name', None)
        ticket_id = dispatch.get('Ext_Ref_Num__c', None)

        onsite_time_needed = self.get_onsite_time_needed(dispatch)
        onsite_timezone = self.get_onsite_timezone(dispatch)

        if onsite_time_needed is None or onsite_timezone is None:
            self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                              f"- Error: Time and timezone from description: {onsite_time_needed} - {onsite_timezone}")
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
