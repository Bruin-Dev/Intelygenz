from shortuuid import uuid
import datetime
from pytz import timezone
import re

from phonenumbers import NumberParseException
import phonenumbers

from application.repositories import nats_error_response

from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_2_hours_before_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_12_hours_before_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_12_hours_before_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_2_hours_before_sms
from application.templates.lit.sms.tech_on_site import lit_get_tech_on_site_sms
from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_sms_tech_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_sms_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_12_hours_before_sms_tech_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_2_hours_before_sms_tech_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_12_hours_before_sms_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_2_hours_before_sms_note
from application.templates.lit.lit_tech_on_site import lit_get_tech_on_site_note

from application.repositories.utils_repository import UtilsRepository


class LitRepository:
    def __init__(self, logger, config, event_bus, notifications_repository, bruin_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository
        self.DATETIME_TZ_FORMAT = "%Y-%m-%d %I:%M%p"
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
        self._dispatch_statuses = [
            self.DISPATCH_REQUESTED,
            self.DISPATCH_CONFIRMED,
            self.DISPATCH_FIELD_ENGINEER_ON_SITE,
            self.DISPATCH_REPAIR_COMPLETED
        ]

    async def get_all_dispatches(self):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(f'Getting all dispatches from LIT...')
            response = await self._event_bus.rpc_request("lit.dispatch.get", request, timeout=60)
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

    @staticmethod
    def get_sms_to_tech(dispatch):
        # Example format->  Job_Site_Contact_Name_and_Phone_Number: "Jane Doe +1 666 6666 666"
        sms_to = dispatch.get('Tech_Mobile_Number')
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
            'timezone': final_timezone,
            'datetime_formatted_str': return_datetime_localized.strftime(UtilsRepository.DATETIME_FORMAT)
        }

    def is_dispatch_confirmed(self, dispatch):
        # A confirmed dispatch must have status: 'Request Confirmed'
        # and this two fields filled Tech_First_Name, Tech_Mobile_Number
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_CONFIRMED,
                    dispatch.get("Tech_First_Name") is not None,
                    dispatch.get("Tech_Mobile_Number") is not None])

    def is_tech_on_site(self, dispatch):
        # Filter tech on site dispatches
        # Dispatch Confirmed --> Field Engineer On Site:
        # Tech_Arrived_On_Site is set to true and Time_of_Check_In is set.
        # Bruin Note:*#Automation Engine#*Dispatch Management - Field Engineer On Site<FE Name> has arrived
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_FIELD_ENGINEER_ON_SITE,
                    dispatch.get("Tech_Arrived_On_Site") is not None,
                    dispatch.get("Tech_Arrived_On_Site") is True,
                    dispatch.get("Time_of_Check_In") is not None])

    def is_repair_completed(self, dispatch):
        # Field Engineer On Site --> Repair Completed: Tech_Off_Site is set to true and Time_of_Check_Out is set.
        # Bruin Note:
        # *#Automation Engine#*
        # Dispatch Management - Repair Completed
        #
        # Dispatch request for Mar 16, 2020 @ 07:00 AM Eastern has been completed.
        # Reference: 4585231
        return all([dispatch is not None,
                    dispatch.get('Dispatch_Status') == self.DISPATCH_REPAIR_COMPLETED,
                    dispatch.get("Tech_Arrived_On_Site") is not None,
                    dispatch.get("Tech_Arrived_On_Site") is True,
                    dispatch.get("Time_of_Check_In") is not None,
                    dispatch.get("Time_of_Check_Out") is not None])

    def get_dispatches_splitted_by_status(self, dispatches):
        dispatches_splitted_by_status = {}
        for ds in self._dispatch_statuses:
            dispatches_splitted_by_status[ds] = []
        for dispatch in dispatches:
            if dispatch.get('Dispatch_Status') in self._dispatch_statuses:
                dispatches_splitted_by_status[dispatch.get('Dispatch_Status')].append(dispatch)
        return dispatches_splitted_by_status

    async def send_confirmed_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local')
        }

        sms_data = lit_get_dispatch_confirmed_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending Confirmed SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def send_confirmed_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'site': dispatch.get('Job_Site'),
            'street': dispatch.get('Job_Site_Street')
        }

        sms_data = lit_get_dispatch_confirmed_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS tech to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS tech: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending Confirmed SMS tech with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS tech sent Response {sms_response_body}")
        return True

    async def send_tech_12_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_12_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 12 hours SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def send_tech_12_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to,
            'site': dispatch.get('Job_Site'),
            'street': dispatch.get('Job_Site_Street')
        }

        sms_data = lit_get_tech_12_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS tech to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS tech: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 12 hours SMS tech with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS tech sent Response {sms_response_body}")
        return True

    async def send_tech_2_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to
        }

        sms_data = lit_get_tech_2_hours_before_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 2 hours SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def send_tech_2_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'phone_number': sms_to,
            'site': dispatch.get('Job_Site'),
            'street': dispatch.get('Job_Site_Street')
        }

        sms_data = lit_get_tech_2_hours_before_sms_tech(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS tech to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS tech: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech 2 hours SMS tech with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS tech sent Response {sms_response_body}")
        return True

    async def send_tech_on_site_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'field_engineer_name': dispatch.get('Tech_First_Name')
        }

        sms_data = lit_get_tech_on_site_sms(sms_data_payload)

        sms_payload = {
            'sms_to': sms_to.replace('+', ''),
            'sms_data': sms_data
        }
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_data}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_data}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech on site SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def append_confirmed_note(self, dispatch_number, ticket_id, dispatch) -> bool:
        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                          f"- Adding confirm note")
        note_data = {
            'vendor': 'LIT',
            'dispatch_number': dispatch_number,
            'date_of_dispatch': dispatch.get('Date_of_Dispatch'),
            'time_of_dispatch': dispatch.get('Hard_Time_of_Dispatch_Local'),
            'time_zone': dispatch.get('Hard_Time_of_Dispatch_Time_Zone_Local'),
            'tech_name': dispatch.get('Tech_First_Name'),
            'tech_phone': dispatch.get('Tech_Mobile_Number')
        }
        note = lit_get_dispatch_confirmed_note(note_data)
        # if self._config.DISPATCH_MONITOR_CONFIG['environment'] == 'production':
        append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)

        append_note_response_status = append_note_response['status']
        append_note_response_body = append_note_response['body']
        if append_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - Not appended")
            err_msg = f'An error occurred when appending a confirmed note with bruin client. ' \
                      f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed note appended")
        self._logger.info(
            f"Confirmed Note appended. Response {append_note_response_body}")
        return True

    async def append_confirmed_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_dispatch_confirmed_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{sms_note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS Confirmed note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS Confirmed note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed SMS note Appended")
        self._logger.info(
            f"SMS Confirmed note appended. Response {append_sms_note_response_body}")
        return True

    async def append_confirmed_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_dispatch_confirmed_sms_tech_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{sms_note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - Tech SMS Confirmed note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- Tech SMS Confirmed note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed Tech SMS note Appended")
        self._logger.info(
            f"SMS Tech Confirmed note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_12_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_12_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} "
                              f"Note: `{sms_note}` "
                              f"- SMS tech 12 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS 12 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 12h note Appended")
        self._logger.info(
            f"SMS 12h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_12_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_12_hours_before_sms_tech_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} "
                              f"Note: `{sms_note}` "
                              f"- SMS tech 12 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech 12 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 12h note Appended")
        self._logger.info(
            f"SMS tech 12h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_2_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_2_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS 2 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS 2 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 2h note Appended")
        self._logger.info(
            f"SMS 2h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_2_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'phone_number': sms_to
        }
        sms_note = lit_get_tech_2_hours_before_sms_tech_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS tech 2 hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech 2 hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS 2h note Appended")
        self._logger.info(
            f"SMS tech 2h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_on_site_sms_note(self, dispatch_number, ticket_id, sms_to, field_engineer_name) -> bool:
        sms_note_data = {
            'dispatch_number': dispatch_number,
            'field_engineer_name': field_engineer_name,
            'phone': sms_to
        }
        sms_note = lit_get_tech_on_site_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS tech on site note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS tech on site note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS tech on site note Appended")
        self._logger.info(
            f"Tech on site note appended. Response {append_sms_note_response_body}")
        return True
