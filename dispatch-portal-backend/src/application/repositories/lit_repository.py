import base64
import datetime
from pytz import timezone
import re
from shortuuid import uuid

from application.repositories.utils_repository import UtilsRepository
from application.repositories import nats_error_response


class LitRepository:
    def __init__(self, logger, config, event_bus, notifications_repository, bruin_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository
        self.DATETIME_TZ_FORMAT = "%Y-%m-%d %I:%M%p"
        self.DATETIME_FORMAT = '%b %d, %Y @ %I:%M %p {time_zone_of_dispatch}'
        self._reg = r"\d(\d)?([:,]\d\d)?[( )|(-)]?((am)|(AM)|(Am)|(aM)|(pm)|(PM)|(Pm)|(pM)|(P)|(p)|(A)|(a))?"
        self._compiled = re.compile(self._reg)
        self._reg_am_pm = r"((am)|(AM)|(Am)|(pm)|(PM)|(Pm)|(P)|(p)|(A)|(a))"
        self._compiled_am_pm = re.compile(self._reg_am_pm)
        self._reg_time = r"\d(\d)?([:,]\d\d)?((am)|(AM)|(Am)|(pm)|(PM)|(Pm))?"
        self._compiled_time = re.compile(self._reg_time)
        # Dispatch Statuses
        self.DISPATCH_REQUESTED = 'New Dispatch'
        self.DISPATCH_CONFIRMED = 'Request Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'Tech Arrived'
        self.DISPATCH_REPAIR_COMPLETED = 'Close Out'

    def get_dispatch_confirmed_date_time_localized(self, dispatch):
        return_datetime_localized = None
        try:
            date_of_dispatch = dispatch.get('Date_of_Dispatch', None)
            time_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Local', None)
            time_zone_of_dispatch = dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local', None)
            self._logger.info(f"Date_of_dispatch: {date_of_dispatch} - time_of_dispatch: {time_of_dispatch}")
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
            self._logger.error(f"Error: getting confirmed date time of dispatch -> {ex}")
            return None

        return {
            'datetime_localized': return_datetime_localized,
            'timezone': final_timezone,
            'datetime_formatted_str': return_datetime_localized.strftime(
                self.DATETIME_FORMAT.format(time_zone_of_dispatch=time_zone_of_dispatch))
        }

    async def get_dispatch(self, dispatch_number=None, igz_dispatches_only=False):
        err_msg = None

        payload = {
            "request_id": uuid(),
            "body": {},
        }

        if dispatch_number:
            payload['body']['dispatch_number'] = dispatch_number

        if igz_dispatches_only:
            payload['body']['igz_dispatches_only'] = igz_dispatches_only

        try:
            if dispatch_number:
                self._logger.info(f'Getting dispatch {dispatch_number} from LIT...')
            else:
                self._logger.info('Getting all dispatches from LIT...')

            response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)
        except Exception as e:
            if dispatch_number:
                err_msg = f'An error occurred when trying to get dispatch {dispatch_number} from LIT -> {e}'
            else:
                err_msg = f'An error occurred when trying to get all dispatches from LIT -> {e}'

            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                if dispatch_number:
                    err_msg = (
                        f'Error while trying to get dispatch {dispatch_number} from LIT in environment '
                        f'{self._config.ENVIRONMENT_NAME.upper()}: Error {response_status} - {response_body}'
                    )
                else:
                    err_msg = (
                        f'Error while trying to get all dispatches from LIT in environment '
                        f'{self._config.ENVIRONMENT_NAME.upper()}: Error {response_status} - {response_body}'
                    )
            else:
                if dispatch_number:
                    self._logger.info(f"Got dispatch {dispatch_number} from LIT successfully!")
                else:
                    self._logger.info(f"Got all dispatches from LIT successfully!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def update_dispatch(self, dispatch_request=None):
        err_msg = None

        payload = {
            "request_id": uuid(),
            "body": {
                'RequestDispatch': dispatch_request,
            },
        }

        try:
            self._logger.info(f'Updating LIT dispatch using payload {dispatch_request}...')
            response = await self._event_bus.rpc_request("lit.dispatch.update", payload, timeout=30)
        except Exception as e:
            err_msg = f'An error occurred when trying to update LIT dispatch using payload {dispatch_request} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while trying to update LIT dispatch using payload {dispatch_request} in environment '
                    f'{self._config.ENVIRONMENT_NAME.upper()}: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f"Updated LIT dispatch using payload {dispatch_request} successfully!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_dispatch(self, dispatch_request=None):
        err_msg = None

        payload = {
            "request_id": uuid(),
            "body": {
                'RequestDispatch': dispatch_request,
            },
        }

        try:
            self._logger.info(f'Creating LIT dispatch using payload {dispatch_request}...')
            response = await self._event_bus.rpc_request("lit.dispatch.post", payload, timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when trying to create LIT dispatch using payload {dispatch_request} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while trying to create LIT dispatch using payload {dispatch_request} in environment '
                    f'{self._config.ENVIRONMENT_NAME.upper()}: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f"Created LIT dispatch using payload {dispatch_request} successfully!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def update_file_to_dispatch(self, dispatch_number=None, body=None, file_name=None):
        err_msg = None

        payload = {
            "request_id": uuid(),
            "body": {
                'dispatch_number': dispatch_number,
                'payload': base64.b64encode(body).decode('utf-8'),
                'file_name': file_name,
            },
        }

        try:
            self._logger.info(f'Uploading file {file_name} to LIT dispatch {dispatch_number}...')
            response = await self._event_bus.rpc_request("lit.dispatch.upload.file", payload, timeout=30)
        except Exception as e:
            err_msg = (
                f'An error occurred when trying to upload file {file_name} to LIT dispatch {dispatch_number}" -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while trying to upload file {file_name} to LIT dispatch {dispatch_number} in environment '
                    f'{self._config.ENVIRONMENT_NAME.upper()}: Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f"Uploaded file {file_name} to LIT dispatch {dispatch_number} successfully!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
