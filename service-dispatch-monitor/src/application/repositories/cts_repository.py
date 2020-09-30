from datetime import datetime
import phonenumbers
import iso8601
import pytz
import re
from phonenumbers import NumberParseException
from shortuuid import uuid
from datetime import datetime
from pytz import timezone

from application.templates.cts.cts_dispatch_cancel import cts_get_dispatch_cancel_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech_note
from application.templates.cts.cts_tech_on_site import cts_get_tech_on_site_note
from application.templates.cts.cts_updated_tech import cts_get_updated_tech_note
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms
from application.templates.cts.sms.updated_tech import cts_get_updated_tech_sms, cts_get_updated_tech_sms_tech

from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_x_hours_before_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_x_hours_before_sms_tech_note
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_x_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_x_hours_before_sms


from application.repositories import nats_error_response
from application.repositories.utils_repository import UtilsRepository


class CtsRepository:
    def __init__(self, logger, config, event_bus, notifications_repository, bruin_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository

        self.DATETIME_FORMAT = '%b %d, %Y @ %I:%M %p UTC'

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.IGZ_DN_WATERMARK = 'IGZ'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'

        self.HOURS_12 = 12.0
        self.HOURS_6 = 6.0
        self.HOURS_2 = 2.0

        # Dispatch Statuses
        self.DISPATCH_REQUESTED = 'Open'
        self.DISPATCH_CONFIRMED = 'Scheduled'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'On Site'
        self.DISPATCH_REPAIR_COMPLETED = 'Completed'
        self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL = 'Complete Pending Collateral'
        self.DISPATCH_SUBMITTED_FOR_BILLING = 'Submitted for Billing'
        self.DISPATCH_BILLED = 'Billed'
        self.DISPATCH_ON_HOLD = 'On Hold'
        self.DISPATCH_CANCELLED = 'Canceled'
        self.DISPATCH_RESCHEDULE = 'Reschedule'
        self._dispatch_statuses = [
            self.DISPATCH_REQUESTED,
            self.DISPATCH_CONFIRMED,
            self.DISPATCH_FIELD_ENGINEER_ON_SITE,
            self.DISPATCH_REPAIR_COMPLETED,
            self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL,
            self.DISPATCH_CANCELLED
        ]

        # Reminders
        self.TECH_12_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 12h prior reminder SMS'
        self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 12h prior reminder tech SMS'
        self.TECH_6_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 6h prior reminder SMS'
        self.TECH_6_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 6h prior reminder tech SMS'
        self.TECH_2_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 2h prior reminder SMS'
        self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 2h prior reminder tech SMS'
        self._reminders = [
            {
                "hour": self.HOURS_12,
                "type": "client",
                "watermark": self.TECH_12_HOURS_BEFORE_SMS_WATERMARK
            },
            {
                "hour": self.HOURS_12,
                "type": "tech",
                "watermark": self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK
            },
            {
                "hour": self.HOURS_6,
                "type": "client",
                "watermark": self.TECH_6_HOURS_BEFORE_SMS_WATERMARK
            },
            {
                "hour": self.HOURS_6,
                "type": "tech",
                "watermark": self.TECH_6_HOURS_BEFORE_SMS_TECH_WATERMARK
            },
            {
                "hour": self.HOURS_2,
                "type": "client",
                "watermark": self.TECH_2_HOURS_BEFORE_SMS_WATERMARK
            },
            {
                "hour": self.HOURS_2,
                "type": "tech",
                "watermark": self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK
            }
        ]

    async def get_all_dispatches(self):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(f'Getting all dispatches from CTS...')
            response = await self._event_bus.rpc_request("cts.dispatch.get", request, timeout=60)
            self._logger.info(f'Got all dispatches from CTS!')
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all dispatches from CTS -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving all tickets from CTS in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def get_sms_to(dispatch):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        # Find sms to number
        sms_to = None
        for line in description_lines:
            if line and len(line) > 0 and 'Contact #:' in line:
                sms_to = ''.join(ch for ch in line if ch.isdigit())
                break
        if sms_to is None or sms_to.strip() == '':
            return None
        try:
            # TODO: check other countries
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None

    @staticmethod
    def get_sms_to_from_note(note):
        if not note:
            return None
        description_lines = note.splitlines()
        sms_to = None
        for line in description_lines:
            if line and len(line) > 0 and 'Phone: ' in line:
                sms_to = ''.join(ch for ch in line if ch.isdigit())
                break
        if sms_to is None or sms_to.strip() == '':
            return None
        try:
            # TODO: check other countries
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None

    @staticmethod
    def get_onsite_contact(dispatch):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        onsite_contact = None
        for line in description_lines:
            if line and len(line) > 0 and 'Onsite Contact:' in line:
                onsite_contact = ''.join(ch for ch in line)
                break
        if onsite_contact is None or onsite_contact.strip() == '':
            return None
        return onsite_contact.strip().replace('Onsite Contact: ', '')

    @staticmethod
    def get_onsite_contact_from_note(note):
        if not note:
            return None
        description_lines = note.splitlines()
        onsite_contact = None
        for line in description_lines:
            if line and len(line) > 0 and 'On-Site Contact:' in line:
                onsite_contact = ''.join(ch for ch in line)
                break
        if onsite_contact is None or onsite_contact.strip() == '':
            return None
        return onsite_contact.strip().replace('On-Site Contact: ', '')

    @staticmethod
    def get_location(dispatch):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        location = None
        for line in description_lines:
            if line and len(line) > 0 and 'Location ID:' in line:
                location = ''.join(ch for ch in line)
                break
        if location is None or location.strip() == '':
            return None
        return location.strip().replace('Location ID: ', '')

    @staticmethod
    def get_location_from_note(note):
        if not note:
            return None
        description_lines = note.splitlines()
        location = None
        for line in description_lines:
            if line and len(line) > 0 and 'Address:' in line:
                location = ''.join(ch for ch in line)
                break
        if location is None or location.strip() == '':
            return None
        return location.strip().replace('Address: ', '')

    @staticmethod
    def get_sms_to_tech(dispatch):
        # Example format->  Resource_Phone_Number__c: "+1 666 6666 666"
        sms_to = dispatch.get('Resource_Phone_Number__c')
        if sms_to is None or sms_to.strip() == '':
            return None
        # Remove non digits
        sms_to = ''.join(ch for ch in sms_to if ch.isdigit())
        try:
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None

    def is_dispatch_confirmed(self, dispatch):
        # A confirmed dispatch must have status: 'Scheduled'
        # Confirmed__c set to True, API_Resource_Name__c and Resource_Phone_Number__c not None
        return all([dispatch is not None,
                    # dispatch.get('Confirmed__c') is True,
                    dispatch.get('Status__c') in self.DISPATCH_CONFIRMED,
                    dispatch.get("API_Resource_Name__c") is not None,
                    dispatch.get("Resource_Phone_Number__c") is not None])

    def is_tech_on_site(self, dispatch):
        # Filter tech on site dispatches
        # Dispatch Confirmed --> Field Engineer On Site:
        # Status__c and Check_In_Date__c is not None
        # Bruin Note:*#Automation Engine#*Dispatch Management - Field Engineer On Site<FE Name> has arrived
        return all([dispatch is not None,
                    dispatch.get('Status__c') == self.DISPATCH_FIELD_ENGINEER_ON_SITE,
                    dispatch.get("Check_In_Date__c") is not None])

    def is_dispatch_cancelled(self, dispatch):
        return all([dispatch is not None, dispatch.get('Status__c') == self.DISPATCH_CANCELLED])

    def get_dispatches_splitted_by_status(self, dispatches):
        dispatches_splitted_by_status = {}
        for ds in self._dispatch_statuses:
            dispatches_splitted_by_status[ds] = []
        for dispatch in dispatches:
            if dispatch.get('Status__c') in self._dispatch_statuses:
                dispatches_splitted_by_status[dispatch.get('Status__c')].append(dispatch)
        return dispatches_splitted_by_status

    async def send_confirmed_sms(self, dispatch_number, ticket_id, dispatch_datetime, sms_to, tech_name) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'tech_name': tech_name
        }

        sms_data = cts_get_dispatch_confirmed_sms(sms_data_payload)

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

    async def send_confirmed_sms_tech(self, dispatch_number, ticket_id, dispatch, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'site': dispatch.get('Lookup_Location_Owner__c'),
            'street': dispatch.get('Street__c')
        }

        sms_data = cts_get_dispatch_confirmed_sms_tech(sms_data_payload)

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

    async def send_sms(self, dispatch_number, ticket_id, sms_to, current_hour, sms_data_payload, sms_payload):
        self._logger.info(f"Sending SMS to {sms_to} with data: `{sms_payload['sms_data']}`")
        sms_response = await self._notifications_repository.send_sms(sms_payload)
        sms_response_status = sms_response['status']
        sms_response_body = sms_response['body']
        if sms_response_status not in range(200, 300):
            self._logger.info(f"SMS: `{sms_payload['sms_data']}` TO: {sms_to} "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - SMS NOT sent")
            err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                      f'An error occurred when sending a tech {current_hour} hours SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS sent Response {sms_response_body}")
        return True

    async def send_tech_on_site_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'field_engineer_name': dispatch.get('API_Resource_Name__c')
        }

        sms_data = cts_get_tech_on_site_sms(sms_data_payload)

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

    async def send_updated_tech_sms(
            self, dispatch_number, ticket_id, dispatch, dispatch_datetime, sms_to, tech_name) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'tech_name': tech_name
        }

        sms_data = cts_get_updated_tech_sms(sms_data_payload)

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
                      f'An error occurred when sending Updated tech SMS with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"SMS sent Response {sms_response_body}")
        return True

    async def send_updated_tech_sms_tech(
            self, dispatch_number, ticket_id, dispatch, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'site': dispatch.get('Lookup_Location_Owner__c'),
            'street': dispatch.get('Street__c')
        }

        sms_data = cts_get_updated_tech_sms_tech(sms_data_payload)

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
                      f'An error occurred when sending Updated tech SMS tech with notifier client. ' \
                      f'payload: {sms_payload}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(
            f"SMS tech sent Response {sms_response_body}")
        return True

    async def append_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to, current_hour, sms_note):
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} "
                              f"Note: `{sms_note}` "
                              f"- SMS {current_hour} hours note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` " \
                      f"- SMS {current_hour} hours note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - SMS {current_hour}h note Appended")
        self._logger.info(
            f"SMS {current_hour}h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_confirmed_note(self, dispatch_number, igz_dispatch_number, ticket_id, dispatch) -> bool:
        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                          f"- Adding confirm note")
        note_data = {
            'vendor': 'CTS',
            'dispatch_number': igz_dispatch_number,
            'date_of_dispatch': dispatch.get('Local_Site_Time__c'),
            'tech_name': dispatch.get('API_Resource_Name__c'),
            'tech_phone': dispatch.get('Resource_Phone_Number__c')
        }
        note = cts_get_dispatch_confirmed_note(note_data)

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

    async def append_confirmed_sms_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_note(sms_note_data)
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

    async def append_confirmed_sms_tech_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_dispatch_confirmed_sms_tech_note(sms_note_data)
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
            # await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed Tech SMS note Appended")
        self._logger.info(
            f"SMS Tech Confirmed note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_on_site_sms_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to,
                                           field_engineer_name) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'field_engineer_name': field_engineer_name,
            'phone': sms_to
        }
        sms_note = cts_get_tech_on_site_note(sms_note_data)
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

    async def append_dispatch_cancelled_note(
            self, dispatch_number, igz_dispatch_number, ticket_id, dispatch_datetime_str) -> bool:
        cancelled_note_data = {
            'dispatch_number': igz_dispatch_number,
            'date_of_dispatch': dispatch_datetime_str
        }
        cancelled_note = cts_get_dispatch_cancel_note(cancelled_note_data)
        append_cancelled_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, cancelled_note)
        append_sms_note_response_status = append_cancelled_note_response['status']
        append_sms_note_response_body = append_cancelled_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{cancelled_note}` "
                              f"- Cancelled note not appended")
            err_msg = f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{cancelled_note}` " \
                      f"- Cancelled note not appended"
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{cancelled_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Cancelled note Appended")
        self._logger.info(
            f"Cancelled note appended. Response: {append_sms_note_response_body}")
        return True

    async def append_updated_tech_note(self, dispatch_number, ticket_id, dispatch) -> bool:
        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                          f"- Adding updated tech note")
        note_data = {
            'vendor': 'CTS',
            'dispatch_number': dispatch_number,
            'ticket_id': ticket_id,
            'tech_name': dispatch.get('API_Resource_Name__c'),
            'tech_phone': dispatch.get('Resource_Phone_Number__c')
        }
        note = cts_get_updated_tech_note(note_data)

        append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)

        append_note_response_status = append_note_response['status']
        append_note_response_body = append_note_response['body']
        if append_note_response_status not in range(200, 300):
            self._logger.info(f"Note: `{note}` "
                              f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - Not appended")
            err_msg = f'An error occurred when appending an updated tech note with bruin client. ' \
                      f'Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - payload: {note_data}'
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Updated tech note appended")
        self._logger.info(
            f"Updated tech Note appended. Response {append_note_response_body}")
        return True

    def get_latest_tech_name_assigned_from_notes(self, updated_tech_notes, filtered_ticket_notes, watermark):
        for ticket_note in filtered_ticket_notes:
            if watermark in ticket_note.get('noteValue'):
                updated_tech_notes.append(ticket_note)

        tech_names = []
        for note in updated_tech_notes:
            note_data = note.get('noteValue').splitlines()
            if note_data and 'The Field Engineer' in note_data and \
                    (note_data.index('The Field Engineer') + 1) < len(note_data):
                tech_names.append(note_data[note_data.index('The Field Engineer') + 1])
            elif note_data and 'Field Engineer' in note_data and \
                    (note_data.index('Field Engineer') + 1) < len(note_data):
                tech_names.append(note_data[note_data.index('Field Engineer') + 1])

        latest_tech_name_assigned = tech_names[-1] if len(tech_names) >= 1 else None
        return latest_tech_name_assigned

    @staticmethod
    def get_igz_dispatch_number(dispatch):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        igz_dispatch_number = None
        for line in description_lines:
            if line and len(line) > 0 and 'IGZ Dispatch Number:' in line:
                igz_dispatch_number = ''.join(ch for ch in line)
                break
        if igz_dispatch_number is None or igz_dispatch_number.strip() == '':
            return None
        return igz_dispatch_number.strip().replace('IGZ Dispatch Number: ', '')

    def filter_ticket_notes_by_dispatch_number(self, ticket_notes, dispatch_number):
        filtered_ticket_notes = []
        for note in ticket_notes:
            note_dispatch_number = UtilsRepository.find_dispatch_number_watermark(note,
                                                                                  dispatch_number,
                                                                                  self.MAIN_WATERMARK)
            if len(note_dispatch_number) == 0:
                continue
            filtered_ticket_notes.append(note)

        return filtered_ticket_notes

    def split_ticket_notes_by_igz_dispatch_num(self, filtered_ticket_notes):
        igz_dispatch_numbers = set()
        splitted_ticket_notes = {}

        for ticket_note in filtered_ticket_notes:
            if ticket_note and ticket_note.get('noteValue') and \
                    self.DISPATCH_REQUESTED_WATERMARK in ticket_note.get('noteValue'):
                _igz_dispatch_number = UtilsRepository.find_dispatch_number_watermark(ticket_note,
                                                                                      self.IGZ_DN_WATERMARK,
                                                                                      self.MAIN_WATERMARK)
                if _igz_dispatch_number and _igz_dispatch_number not in splitted_ticket_notes:
                    splitted_ticket_notes[_igz_dispatch_number] = []
                    igz_dispatch_numbers.add(_igz_dispatch_number)
                    splitted_ticket_notes[_igz_dispatch_number] = \
                        self.filter_ticket_notes_by_dispatch_number(filtered_ticket_notes, _igz_dispatch_number)

        return splitted_ticket_notes

    def _find_field_in_dispatch_description(self, dispatch, field_name):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        location = None
        for line in description_lines:
            if line and len(line) > 0 and field_name in line:
                location = ''.join(ch for ch in line)
                break
        if location is None or location.strip() == '':
            return None
        return location.strip().replace(f'{field_name}: ', '')

    def get_onsite_time_needed(self, dispatch):
        onsite_time_needed = self._find_field_in_dispatch_description(dispatch, 'Onsite Time Needed')

        current_hour = re.search(" (.*?)\\.", onsite_time_needed).group(1)
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

    def get_dispatch_confirmed_date_time_localized(self, dispatch, dispatch_number, ticket_id):

        # https://intelygenz.atlassian.net/browse/MET-559

        onsite_time_needed = self.get_onsite_time_needed(dispatch)
        onsite_timezone = self.get_onsite_timezone(dispatch)

        if onsite_time_needed is None or onsite_timezone is None:
            return None

        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                          f"- Time and timezone from description: {onsite_time_needed} - {onsite_timezone}")

        # Convert date to UTC
        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                          f"- Converting: {onsite_time_needed} to UTC")

        date_time_of_dispatch_localized = onsite_timezone.localize(onsite_time_needed)
        date_time_of_dispatch_localized = date_time_of_dispatch_localized.astimezone(pytz.utc)
        datetime_formatted_str = date_time_of_dispatch_localized.strftime(self.DATETIME_FORMAT)

        response = {
            'date_time_of_dispatch_localized': date_time_of_dispatch_localized,
            'timezone': onsite_timezone,
            'datetime_formatted_str': datetime_formatted_str
        }

        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                          f"- Converted: {response}")

        return response

    async def check_reminders(self, dispatch, igz_dispatch_number, filtered_ticket_notes,
                              date_time_of_dispatch_localized, datetime_formatted_str, sms_to, sms_to_tech):
        dispatch_number = dispatch.get('Name', None)
        ticket_id = dispatch.get('Ext_Ref_Num__c', None)
        self._logger.info("[service-dispatch-monitor] [CTS] Checking reminders")

        for reminder in self._reminders:
            current_hour = reminder['hour']
            pre_log = f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - IGZ: {igz_dispatch_number} - " \
                      f"Reminder {int(current_hour)} hours for {reminder['type']}"
            try:
                self._logger.info(pre_log)

                reminder_note_found = UtilsRepository.find_note(filtered_ticket_notes, reminder['watermark'])
                if reminder_note_found:
                    self._logger.info(f"{pre_log} - Has already the reminder note")
                    continue
                self._logger.info(f"{pre_log} - Dispatch has no notes for this reminder, "
                                  f"checking if it is needed to send sms and note")

                just_now = datetime.now(pytz.utc)
                hours_diff = UtilsRepository.get_diff_hours_between_datetimes(just_now, date_time_of_dispatch_localized)

                should_send = UtilsRepository.in_range(hours_diff, current_hour - 1, current_hour)
                self._logger.info(f"{pre_log} - UTC - dt: {date_time_of_dispatch_localized} - "
                                  f"now: {just_now} - diff: {hours_diff}")
                if not should_send:
                    self._logger.info(f"{pre_log} - SMS note not needed to send now")
                    continue

                self._logger.info(f"{pre_log} - Sending SMS and appending note")

                if reminder['type'] == 'client':
                    current_sms_to = sms_to
                    sms_data_payload = {
                        'date_of_dispatch': datetime_formatted_str,
                        'phone_number': current_sms_to,
                        'hours': int(current_hour)
                    }
                    sms_data = cts_get_tech_x_hours_before_sms(sms_data_payload)
                else:
                    current_sms_to = sms_to_tech
                    sms_data_payload = {
                        'date_of_dispatch': datetime_formatted_str,
                        'phone_number': current_sms_to,
                        'site': dispatch.get('Lookup_Location_Owner__c'),
                        'street': dispatch.get('Street__c'),
                        'hours': int(current_hour)
                    }
                    sms_data = cts_get_tech_x_hours_before_sms_tech(sms_data_payload)

                sms_payload = {
                    'sms_to': sms_to.replace('+', ''),
                    'sms_data': sms_data
                }
                result_sms_sended = await self.send_sms(
                    dispatch_number, ticket_id, current_sms_to, current_hour, sms_data_payload, sms_payload)
                if not result_sms_sended:
                    msg = f"[service-dispatch-monitor] [CTS] " \
                          f"{pre_log} - SMS {current_hour}h not sended"
                else:
                    sms_note_data = {
                        'dispatch_number': igz_dispatch_number,
                        'phone_number': current_sms_to,
                        'hours': int(current_hour)
                    }
                    if reminder['type'] == 'client':
                        sms_note = cts_get_tech_x_hours_before_sms_note(sms_note_data)
                    else:
                        sms_note = cts_get_tech_x_hours_before_sms_tech_note(sms_note_data)

                    result_append_sms_note = await self.append_note(
                        dispatch_number, igz_dispatch_number, ticket_id, current_sms_to, current_hour, sms_note)
                    if not result_append_sms_note:
                        msg = f"[service-dispatch-monitor] [CTS] {pre_log} - A sms before note not appended"
                    else:
                        msg = f"[service-dispatch-monitor] [CTS] {pre_log} - A sms before note appended"
                self._logger.info(msg)
                await self._notifications_repository.send_slack_message(msg)
            except Exception as ex:
                self._logger.error(f"ERROR: {pre_log} --> {ex}")
