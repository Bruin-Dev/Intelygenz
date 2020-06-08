from phonenumbers import NumberParseException
from shortuuid import uuid
import datetime
from pytz import timezone


import phonenumbers

from application.repositories import nats_error_response


class LitRepository:
    def __init__(self, logger, config, event_bus, notifications_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self.DATETIME_TZ_FORMAT = "%Y-%m-%d %I:%M%p"

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
        except NumberParseException:
            return None
        return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)

    def get_dispatch_confirmed_date_time_localized(self, dispatch, dispatch_number, ticket_id):
        return_datetime_localized = None
        try:
            final_time_of_dispatch = None
            # "2015-01-01"
            date_of_dispatch = dispatch.get('Date_of_Dispatch', None)
            # ['4-6pm', '4pm-6pm','12pm','12:00PM','9:00 AM','10 am','10am ET','10a-12p ET','11a-1p PT','2-4pm ET',
            # '12-2PM CT','11am CT','12:00','3:30pm ET','12::00PM','8am-1p PT','7.00PM','8 AM CT']
            time_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Local', None)

            if time_of_dispatch is None:
                self._logger.error(f"Not valid time of dispatch: {time_of_dispatch}")
                return None

            time_of_dispatch = time_of_dispatch.upper()
            final_time_of_dispatch = None
            am_pm = None
            timezone_job = None

            if '::' in time_of_dispatch:
                time_of_dispatch = time_of_dispatch.replace('::', ':')

            end_time_of_dispatch = None
            if '-' in time_of_dispatch:
                # ['4-6pm', '4pm-6pm', '10a-12p ET', '11a-1p PT', '2-4pm ET', '12-2PM CT', '8am-1p PT']
                if ' ' in time_of_dispatch:
                    time_of_dispatch = time_of_dispatch.split(' ')[0]
                start_time_of_dispatch = time_of_dispatch.split('-')[0]
                end_time_of_dispatch = time_of_dispatch.split('-')[1]
                if 'AM' in start_time_of_dispatch or 'A' in start_time_of_dispatch:
                    am_pm = 'AM'
                    start_time_of_dispatch = start_time_of_dispatch.replace('AM', '')
                    final_time_of_dispatch = start_time_of_dispatch.replace('A', '')
                elif 'PM' in start_time_of_dispatch or 'P' in start_time_of_dispatch:
                    am_pm = 'PM'
                    start_time_of_dispatch = start_time_of_dispatch.replace('PM', '')
                    final_time_of_dispatch = start_time_of_dispatch.replace('P', '')
            else:
                # ['12pm', '12:00PM', '9:00 AM', '10 am', '10am ET', '11am CT',
                #  '12:00', '3:30pm ET', '12::00PM', '7.00PM', '8 AM CT']
                if '.' not in time_of_dispatch:
                    time_of_dispatch = time_of_dispatch.replace('.', ':')
                if 'AM' in time_of_dispatch or 'A' in time_of_dispatch or \
                        'PM' in time_of_dispatch or 'P' in time_of_dispatch:
                    if ' ' in time_of_dispatch:
                        if len(time_of_dispatch.split(' ')) > 2:
                            final_time_of_dispatch = time_of_dispatch.split(' ')[0]
                            am_pm = time_of_dispatch.split(' ')[1]
                            tz_job = time_of_dispatch.split(' ')[2]
                        else:
                            final_time_of_dispatch = time_of_dispatch.split(' ')[0]
                            tz_job = time_of_dispatch.split(' ')[1]
                            if ':' in final_time_of_dispatch:
                                part_final_time_of_dispatch = final_time_of_dispatch.split(':')[0]
                                part_2_final_time_of_dispatch = final_time_of_dispatch.split(':')[1]

                                minutes = ''.join(ch for ch in part_2_final_time_of_dispatch if ch.isdigit())
                                am_pm = ''.join(ch for ch in part_2_final_time_of_dispatch if not ch.isdigit())
                                final_time_of_dispatch = f"{part_final_time_of_dispatch}:{minutes}"
                            else:
                                temp = final_time_of_dispatch
                                final_time_of_dispatch = ''.join(ch for ch in temp if ch.isdigit())
                                am_pm = ''.join(ch for ch in temp if not ch.isdigit())
                    else:
                        final_time_of_dispatch = ''.join(ch for ch in time_of_dispatch if ch.isdigit())
                        am_pm = ''.join(ch for ch in time_of_dispatch if not ch.isdigit())
                else:
                    final_time_of_dispatch = None
            if final_time_of_dispatch is None:
                return None

            if ':' not in final_time_of_dispatch:
                final_time_of_dispatch = f"{final_time_of_dispatch}:00"

            final_datetime = datetime.datetime.strptime(f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}',
                                                        self.DATETIME_TZ_FORMAT)
            # "Pacific Time"
            time_zone_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)
            time_zone_of_dispatch = time_zone_of_dispatch.replace('Time', '').replace(' ', '')
            final_timezone = timezone(f'US/{time_zone_of_dispatch}')

            return_datetime_localized = final_timezone.localize(final_datetime)
        except Exception as ex:
            self._logger.error(f"Error: getting confirmed date time of dispatch -> {ex}")
            return None

        return {
            'datetime_localized': return_datetime_localized,
            'timezone': final_timezone
        }
