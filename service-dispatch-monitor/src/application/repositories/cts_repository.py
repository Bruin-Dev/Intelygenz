from shortuuid import uuid
import re
from phonenumbers import NumberParseException
import phonenumbers

from application.repositories import nats_error_response
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_12_hours_before_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_2_hours_before_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech_note
from application.templates.cts.cts_tech_on_site import cts_get_tech_on_site_note

from application.templates.cts.cts_dispatch_cancel import cts_get_dispatch_cancel_note


class CtsRepository:
    def __init__(self, logger, config, event_bus, notifications_repository, bruin_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository

        # Dispatch Statuses
        self.DISPATCH_REQUESTED = 'Open'
        self.DISPATCH_CONFIRMED = 'Scheduled'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'On Site'
        self.DISPATCH_REPAIR_COMPLETED = 'Completed'
        self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL = 'Complete Pending Collateral'
        self.DISPATCH_SUBMITTED_FOR_BILLING = 'Submitted for Billing'
        self.DISPATCH_BILLED = 'Billed'
        self.DISPATCH_ON_HOLD = 'On Hold'
        self.DISPATCH_CANCELLED = 'Cancelled'
        self.DISPATCH_RESCHEDULE = 'Reschedule'
        self._dispatch_statuses = [
            self.DISPATCH_REQUESTED,
            self.DISPATCH_CONFIRMED,
            self.DISPATCH_FIELD_ENGINEER_ON_SITE,
            self.DISPATCH_REPAIR_COMPLETED,
            self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL,
            self.DISPATCH_CANCELLED
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

    async def send_confirmed_sms(self, dispatch_number, ticket_id, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime
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

    async def send_tech_12_sms(self, dispatch_number, ticket_id, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_12_hours_before_sms(sms_data_payload)

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

    async def send_tech_12_sms_tech(self, dispatch_number, ticket_id, dispatch, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': dispatch.get('Lookup_Location_Owner__c'),
            'street': dispatch.get('Street__c')
        }

        sms_data = cts_get_tech_12_hours_before_sms_tech(sms_data_payload)

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

    async def send_tech_2_sms(self, dispatch_number, ticket_id, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to
        }

        sms_data = cts_get_tech_2_hours_before_sms(sms_data_payload)

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

    async def send_tech_2_sms_tech(self, dispatch_number, ticket_id, dispatch, dispatch_datetime, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch_datetime,
            'phone_number': sms_to,
            'site': dispatch.get('Lookup_Location_Owner__c'),
            'street': dispatch.get('Street__c')
        }

        sms_data = cts_get_tech_2_hours_before_sms_tech(sms_data_payload)

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

    async def append_tech_12_sms_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_tech_12_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} "
                              f"Note: `{sms_note}` "
                              f"- SMS 12 hours note not appended")
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

    async def append_tech_12_sms_tech_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_tech_12_hours_before_sms_tech_note(sms_note_data)
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
                          f"Ticket_id: {ticket_id} - SMS tech 12h note Appended")
        self._logger.info(
            f"SMS tech 12h Note appended. Response {append_sms_note_response_body}")
        return True

    async def append_tech_2_sms_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_tech_2_hours_before_sms_note(sms_note_data)
        append_sms_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id, sms_note)
        append_sms_note_response_status = append_sms_note_response['status']
        append_sms_note_response_body = append_sms_note_response['body']
        if append_sms_note_response_status not in range(200, 300):
            self._logger.info(f"Dispatch: {dispatch_number} Ticket_id: {ticket_id} Note: `{sms_note}` "
                              f"- SMS tech 2 hours note not appended")
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

    async def append_tech_2_sms_tech_note(self, dispatch_number, igz_dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
            'dispatch_number': igz_dispatch_number,
            'phone_number': sms_to
        }
        sms_note = cts_get_tech_2_hours_before_sms_tech_note(sms_note_data)
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

    async def append_dispatch_cancelled_note(self, dispatch_number, igz_dispatch_number, ticket_id, dispatch) -> bool:
        cancelled_note_data = {
            'dispatch_number': igz_dispatch_number,
            'date_of_dispatch': dispatch.get('Local_Site_Time__c')
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
