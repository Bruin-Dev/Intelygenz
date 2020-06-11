from phonenumbers import NumberParseException
from shortuuid import uuid
import datetime
from pytz import timezone
import re


import phonenumbers

from application.repositories import nats_error_response


class LitRepository:
    def __init__(self, logger, config, event_bus, notifications_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self.DATETIME_TZ_FORMAT = "%Y-%m-%d %I:%M%p"
        self._reg = r"\d(\d)?([:,]\d\d)?[( )|(-)]?((am)|(AM)|(Am)|(aM)|(pm)|(PM)|(Pm)|(pM)|(P)|(p)|(A)|(a))?"
        self._compiled = re.compile(self._reg)
        self._reg_am_pm = r"((am)|(AM)|(Am)|(pm)|(PM)|(Pm)|(P)|(p)|(A)|(a))"
        self._compiled_am_pm = re.compile(self._reg_am_pm)
        self._reg_time = r"\d(\d)?([:,]\d\d)?((am)|(AM)|(Am)|(pm)|(PM)|(Pm))?"
        self._compiled_time = re.compile(self._reg_time)

    async def get_all_dispatches(self):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(f'Getting all dispatches from LIT...')
            response = await self._event_bus.rpc_request("lit.dispatch.get", request, timeout=30)
            self._logger.info(f'Got all dispatches from LIT!')
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all dispatches from LIT -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving all tickets from LIT in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def get_sms_to(dispatch):
        # Example format->  Job_Site_Contact_Name_and_Phone_Number: "Jane Doe +1 666 6666 666"
        sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        if sms_to is None or sms_to.strip() == '':
            return None
        # Remove non digits
        sms_to = ''.join(ch for ch in sms_to if ch.isdigit())
        try:
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None

    def get_dispatch_confirmed_date_time_localized(self, dispatch, dispatch_number, ticket_id):
        return_datetime_localized = None
        try:
            date_of_dispatch = dispatch.get('Date_of_Dispatch', None)
            time_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Local', None)
            # time_zone_of_dispatch = dispatch.get('Time_Zone_Local', None)
            time_zone_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)
            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                              f"date_of_dispatch: {date_of_dispatch} - time_of_dispatch: {time_of_dispatch}")
            if time_of_dispatch is None:
                self._logger.error(f"Not valid time of dispatch: {time_of_dispatch}")
                return None
            if time_zone_of_dispatch is None:
                self._logger.error(f"Not valid timezone of dispatch: {time_zone_of_dispatch}")
                return None

            self._logger.info(f"Original time_of_dispatch: {time_of_dispatch}")
            time_of_dispatch = time_of_dispatch.upper()
            # Clean input: '.' -> ':', '::' -> ':'
            time_of_dispatch = time_of_dispatch.replace('.', ':')
            time_of_dispatch = time_of_dispatch.replace('::', ':')
            final_time_of_dispatch = None
            am_pm = None
            self._logger.info(f"Filtered time_of_dispatch: {time_of_dispatch}")
            groups = [x.group() for x in self._compiled.finditer(time_of_dispatch)]
            self._logger.info(groups)
            found_am_pm = False
            for group in groups:
                groups_am_pm = [x.group() for x in self._compiled_am_pm.finditer(group)]
                if not found_am_pm:
                    for group_am_pm in groups_am_pm:
                        if group_am_pm in ['AM', 'PM', 'A', 'P']:
                            found_am_pm = True
                            if 'A' in group_am_pm:
                                am_pm = 'AM'
                            else:
                                am_pm = 'PM'
                            break
            for group in groups:
                groups_time = [x.group() for x in self._compiled_time.finditer(group)]
                if len(groups_time) > 0:
                    final_time_of_dispatch = f'{groups_time[0]}'
                    final_time_of_dispatch = final_time_of_dispatch.replace("AM", "")
                    final_time_of_dispatch = final_time_of_dispatch.replace("PM", "")
                    final_time_of_dispatch = final_time_of_dispatch.replace("A", "")
                    final_time_of_dispatch = final_time_of_dispatch.replace("P", "")
                    if ':' not in final_time_of_dispatch:
                        final_time_of_dispatch = f'{final_time_of_dispatch}:00'
                break
            if found_am_pm:
                new_date = f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}'
                self._logger.info(new_date)
                final_datetime = datetime.datetime.strptime(new_date, self.DATETIME_TZ_FORMAT)
                # "Pacific Time"

                time_zone_of_dispatch = time_zone_of_dispatch.replace('Time', '').replace(' ', '')
                final_timezone = timezone(f'US/{time_zone_of_dispatch}')

                return_datetime_localized = final_timezone.localize(final_datetime)
            else:
                return None
        except Exception as ex:
            self._logger.error(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                               f"Error: getting confirmed date time of dispatch -> {ex}")
            return None

        return {
            'datetime_localized': return_datetime_localized,
            'timezone': final_timezone
        }
