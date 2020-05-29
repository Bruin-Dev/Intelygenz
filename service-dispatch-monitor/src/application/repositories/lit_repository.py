from shortuuid import uuid
import datetime
from pytz import timezone


from application.repositories import nats_error_response


class LitRepository:
    def __init__(self, logger, config, event_bus, notifications_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

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
        # TODO: https://pypi.org/project/phonenumbers/
        # Example format->  Job_Site_Contact_Name_and_Phone_Number: "Jane Doe +1 666 6666 666"
        sms_to = dispatch.get('Job_Site_Contact_Name_and_Phone_Number')
        if sms_to is None or sms_to.strip() == '':
            return None
        # Remove non digits
        sms_to = ''.join(ch for ch in sms_to if ch.isdigit())
        sms_to = f"+{sms_to}"
        if sms_to.strip() == '+':
            return None
        return sms_to

    def get_dispatch_confirmed_date_time_localized(self, dispatch, dispatch_number, ticket_id):
        return_datetime_localized = None
        try:
            # "2015-01-01"
            date_of_dispatch = dispatch.get('Date_of_Dispatch', None)
            # "4pm-6pm"
            time_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Local', None)

            final_time_of_dispatch = None
            start_time_of_dispatch = time_of_dispatch.upper().split('-')[0]
            am_pm = None
            if 'PM' in start_time_of_dispatch:
                am_pm = 'PM'
                final_time_of_dispatch = start_time_of_dispatch.replace('PM', '')
            elif 'AM' in start_time_of_dispatch:
                am_pm = 'AM'
                final_time_of_dispatch = start_time_of_dispatch.replace('AM', '')

            if final_time_of_dispatch is None:
                return None

            if ':' not in final_time_of_dispatch:
                final_time_of_dispatch = f"{final_time_of_dispatch}:00"

            final_datetime = datetime.datetime.strptime(f'{date_of_dispatch} {final_time_of_dispatch}{am_pm}',
                                               "%Y-%m-%d %I:%M%p")

            # "Pacific Time"
            time_zone_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)

            if date_of_dispatch is None or time_of_dispatch is None or time_zone_of_dispatch is None:
                self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                  f"has not valid date '{date_of_dispatch}' or "
                                  f"time '{time_of_dispatch}' or "
                                  f"timezone '{time_zone_of_dispatch}'.")
                return None
            if 'Time' in time_zone_of_dispatch:
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
