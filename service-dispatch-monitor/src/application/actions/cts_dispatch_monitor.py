import asyncio
from datetime import datetime
from time import perf_counter
import iso8601
import pytz
from shortuuid import uuid


from apscheduler.util import undefined
from pytz import timezone

from application.repositories.utils_repository import UtilsRepository
from application.repositories.cts_repository import CtsRepository

from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_12_hours_before_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_2_hours_before_sms_note
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms
from application.templates.cts.sms.tech_on_site import cts_get_tech_on_site_sms
from application.templates.cts.cts_tech_on_site import cts_get_tech_on_site_note


class CtsDispatchMonitor:
    def __init__(self, config, redis_client, event_bus, scheduler, logger, cts_repository, bruin_repository,
                 notifications_repository):
        self._config = config
        self._redis_client = redis_client
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._logger = logger
        self._cts_repository = cts_repository
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository

        self.HOURS_12 = 12
        self.HOURS_2 = 2

        # Dispatch Notes watermarks
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.DISPATCH_CONFIRMED_WATERMARK = 'Dispatch Management - Dispatch Confirmed'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK = 'Dispatch Management - Field Engineer On Site'
        self.DISPATCH_REPAIR_COMPLETED_WATERMARK = 'Dispatch Management - Repair Completed'

        # SMS Notes watermarks
        self.DISPATCH_CONFIRMED_SMS_WATERMARK = 'Dispatch confirmation SMS sent to'
        self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK = 'Dispatch confirmation SMS tech sent to'
        self.TECH_12_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 12h prior reminder SMS'
        self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 12h prior reminder tech SMS'
        self.TECH_2_HOURS_BEFORE_SMS_WATERMARK = 'Dispatch 2h prior reminder SMS'
        self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK = 'Dispatch 2h prior reminder tech SMS'
        self.TECH_ON_SITE_SMS_WATERMARK = 'Dispatch tech on site SMS'

        # Dispatch Statuses
        self.DISPATCH_REQUESTED = 'Open'
        self.DISPATCH_CONFIRMED = 'Scheduled'
        self.DISPATCH_FIELD_ENGINEER_ON_SITE = 'On Site'
        self.DISPATCH_REPAIR_COMPLETED = 'Completed'
        self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL = 'Complete Pending Collateral'
        self.DISPATCH_SUBMITTED_FOR_BILLING = 'Submitted for Billing'
        self.DISPATCH_BILLED = 'Billed'
        self.DISPATCH_ON_HOLD = 'On Hold'
        self.DISPATCH_CANCELED = 'Canceled'
        self.DISPATCH_RESCHEDULE = 'Reschedule'
        self._dispatch_statuses = [
            self.DISPATCH_REQUESTED,
            self.DISPATCH_CONFIRMED,
            self.DISPATCH_FIELD_ENGINEER_ON_SITE,
            self.DISPATCH_REPAIR_COMPLETED,
            self.DISPATCH_REPAIR_COMPLETED_PENDING_COLLATERAL
        ]

        self.SITE_STATUS_REQUIRED_DISPATCH = "Requires Dispatch"

    async def start_monitoring_job(self, exec_on_start):
        self._logger.info('Scheduling Service Dispatch Monitor job for CTS...')
        next_run_time = undefined
        if exec_on_start:
            tz = timezone(self._config.DISPATCH_MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Service Outage Monitor job is going to be executed immediately')

        self._scheduler.add_job(self._cts_dispatch_monitoring_process, 'interval',
                                minutes=self._config.DISPATCH_MONITOR_CONFIG['jobs_intervals']['cts_dispatch_monitor'],
                                next_run_time=next_run_time, replace_existing=False,
                                id='_service_dispatch_monitor_cts_process')

    def _is_dispatch_confirmed(self, dispatch):
        # A confirmed dispatch must have status: 'Scheduled'
        # Confirmed__c set to True, API_Resource_Name__c and Resource_Phone_Number__c not None
        return all([dispatch is not None,
                    dispatch.get('Confirmed__c') is True,
                    dispatch.get('Status__c') in self.DISPATCH_CONFIRMED,
                    dispatch.get("API_Resource_Name__c") is not None,
                    dispatch.get("Resource_Phone_Number__c") is not None])

    def _is_tech_on_site(self, dispatch):
        # Filter tech on site dispatches
        # Dispatch Confirmed --> Field Engineer On Site:
        # Status__c and Check_In_Date__c is not None
        # Bruin Note:*#Automation Engine#*Dispatch Management - Field Engineer On Site<FE Name> has arrived
        return all([dispatch is not None,
                    dispatch.get('Status__c') == self.DISPATCH_FIELD_ENGINEER_ON_SITE,
                    dispatch.get("Check_In_Date__c") is not None])

    def _get_dispatches_splitted_by_status(self, dispatches):
        dispatches_splitted_by_status = {}
        for ds in self._dispatch_statuses:
            dispatches_splitted_by_status[ds] = []
        for dispatch in dispatches:
            if dispatch.get('Status__c') in self._dispatch_statuses:
                dispatches_splitted_by_status[dispatch.get('Status__c')].append(dispatch)
        return dispatches_splitted_by_status

    async def _cts_dispatch_monitoring_process(self):
        try:
            start = perf_counter()
            self._logger.info(f"Starting Dispatch Monitor Process...")
            response_cts_dispatches = await self._cts_repository.get_all_dispatches()
            response_cts_dispatches_status = response_cts_dispatches.get('status')
            response_cts_dispatches_body = response_cts_dispatches.get('body')

            if response_cts_dispatches_status not in range(200, 300):
                self._logger.error("Error getting all dispatches from CTS")
                err_msg = f'An error occurred retrieving all dispatches in the request status from CTS.'
                await self._notifications_repository.send_slack_message(err_msg)
                raise

            if response_cts_dispatches_body is None \
                    or response_cts_dispatches_body['done'] is not True \
                    or 'records' not in response_cts_dispatches_body \
                    or response_cts_dispatches_body['records'] is None:
                self._logger.error(f"[get_all_dispatches] Could not retrieve all dispatches, "
                                   f"reason: {response_cts_dispatches_body}")
                err_msg = f'An error occurred retrieving all dispatches from CTS.'
                await self._notifications_repository.send_slack_message(err_msg)
                return

            cts_dispatches = response_cts_dispatches_body.get('records', [])

            dispatches_splitted_by_status = self._get_dispatches_splitted_by_status(cts_dispatches)

            self._logger.info(f"Splitted by status: {list(dispatches_splitted_by_status.keys())}")

            monitor_tasks = [
                self._monitor_confirmed_dispatches(
                    dispatches_splitted_by_status[self.DISPATCH_CONFIRMED]),
                self._monitor_tech_on_site_dispatches(
                    dispatches_splitted_by_status[self.DISPATCH_FIELD_ENGINEER_ON_SITE])
            ]

            start_monitor_tasks = perf_counter()
            await asyncio.gather(*monitor_tasks, return_exceptions=True)
            stop_monitor_tasks = perf_counter()
            self._logger.info(f"[CTS] All monitor tasks finished: "
                              f"{(stop_monitor_tasks - start_monitor_tasks) / 60} minutes")

            stop = perf_counter()
            self._logger.info(f"[CTS] Elapsed time processing all dispatches: {(stop - start) / 60} minutes")
        except Exception as ex:
            self._logger.error(f"[CTS] Error: {ex}")

    async def _send_confirmed_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c')
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

    async def _send_confirmed_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c')
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

    async def _send_tech_12_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c'),
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

    async def _send_tech_12_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c'),
            'phone_number': sms_to
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

    async def _send_tech_2_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c'),
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

    async def _send_tech_2_sms_tech(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
        if sms_to is None:
            return False

        # Get SMS data
        sms_data_payload = {
            'date_of_dispatch': dispatch.get('Local_Site_Time__c'),
            'phone_number': sms_to
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

    async def _send_tech_on_site_sms(self, dispatch_number, ticket_id, dispatch, sms_to) -> bool:
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

    async def _append_confirmed_note(self, dispatch_number, ticket_id, dispatch) -> bool:
        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                          f"- Adding confirm note")
        note_data = {
            'vendor': 'CTS',
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

    async def _append_confirmed_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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

    async def _append_confirmed_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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
            await self._notifications_repository.send_slack_message(err_msg)
            return False
        self._logger.info(f"Note: `{sms_note}` "
                          f"Dispatch: {dispatch_number} "
                          f"Ticket_id: {ticket_id} - Confirmed Tech SMS note Appended")
        self._logger.info(
            f"SMS Tech Confirmed note appended. Response {append_sms_note_response_body}")
        return True

    async def _append_tech_12_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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

    async def _append_tech_12_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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

    async def _append_tech_2_sms_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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

    async def _append_tech_2_sms_tech_note(self, dispatch_number, ticket_id, sms_to) -> bool:
        sms_note_data = {
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

    async def _append_tech_on_site_sms_note(self, dispatch_number, ticket_id, sms_to, field_engineer_name) -> bool:
        sms_note_data = {
            'field_engineer_name': field_engineer_name
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

    async def _monitor_confirmed_dispatches(self, confirmed_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(confirmed_dispatches)}")
            confirmed_dispatches = list(filter(self._is_dispatch_confirmed, confirmed_dispatches))
            self._logger.info(f"Total confirmed dispatches after filter: {len(confirmed_dispatches)}")

            for dispatch in confirmed_dispatches:
                try:
                    dispatch_number = dispatch.get('Name', None)
                    ticket_id = dispatch.get('Ext_Ref_Num__c', None)

                    self._logger.info(f"Processing Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - {dispatch}")

                    if ticket_id is None or not CtsRepository.is_valid_ticket_id(ticket_id) or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    date_time_of_dispatch = dispatch.get('Local_Site_Time__c')
                    if date_time_of_dispatch is None:
                        self._logger.error(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                           f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Local_Site_Time__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    date_time_of_dispatch_localized = iso8601.parse_date(date_time_of_dispatch, pytz.utc)

                    sms_to = CtsRepository.get_sms_to(dispatch)
                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Description__c')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Description__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    # Tech phonenumber
                    sms_to_tech = CtsRepository.get_sms_to_tech(dispatch)
                    if sms_to_tech is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to_tech' number from: "
                                          f"{dispatch.get('Tech_Mobile_Number')}")
                        err_msg = f"An error occurred retrieve 'sms_to_tech' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Tech_Mobile_Number')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    response = await self._bruin_repository.get_ticket_details(ticket_id)
                    response_status = response['status']
                    response_body = response['body']
                    if response_status not in range(200, 300):
                        self._logger.error(f"Error: Dispatch [{dispatch_number}] "
                                           f"Get ticket details for ticket {ticket_id}: "
                                           f"{response_body}")
                        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue
                    ticket_notes = response_body.get('ticketNotes', [])
                    ticket_notes = [tn for tn in ticket_notes if tn.get('noteValue')]

                    watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    requested_watermark_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    confirmed_sms_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_TECH_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_12_hours_before_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_TECH_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_tech_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_TECH_WATERMARK)

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_tech_note_found: {confirmed_sms_tech_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                                      f"tech_12_hours_before_tech_note_found: {tech_12_hours_before_tech_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_2_hours_before_tech_note_found: {tech_2_hours_before_tech_note_found} ")

                    if watermark_found is None or requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"main_watermark_found: {watermark_found} "
                                      f"requested_watermark_found: {requested_watermark_found} ")
                    # Check if dispatch has a confirmed note
                    if confirmed_note_found is None:
                        result_append_confirmed_note = await self._append_confirmed_note(
                            dispatch_number, ticket_id, dispatch)
                        if not result_append_confirmed_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"Confirmed Note not appended")
                            continue

                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a confirmed note")

                    # Check if dispatch has a sms confirmed note
                    if confirmed_sms_note_found is None:
                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS")
                        sms_sended = await self._send_confirmed_sms(dispatch_number, ticket_id, dispatch, sms_to)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS could not be sent to {sms_to}.")
                            # continue
                        else:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- Confirm SMS note not found")

                            result_append_confirmed_sms_note = await self._append_confirmed_sms_note(
                                dispatch_number, ticket_id, sms_to)

                            if not result_append_confirmed_sms_note:
                                self._logger.info("Confirmed SMS note not appended")
                                # continue
                            else:
                                self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                                  f"Confirmed Note, SMS send and Confirmed SMS note sent OK.")
                            # continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms confirmed note")

                    if confirmed_sms_tech_note_found is None:
                        self._logger.info(f"Dispatch: {dispatch_number} "
                                          f"Ticket_id: {ticket_id} - Sending confirmed SMS Tech")
                        sms_sended = await self._send_confirmed_sms_tech(dispatch_number, ticket_id, dispatch,
                                                                         sms_to_tech)
                        if not sms_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS Tech could not be sent to {sms_to_tech}.")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Confirm SMS tech note not found")

                        result_append_confirmed_sms_note = await self._append_confirmed_sms_tech_note(
                            dispatch_number, ticket_id, sms_to_tech)

                        if not result_append_confirmed_sms_note:
                            self._logger.info("Confirmed SMS tech note not appended")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Confirmed Note, SMS tech send and Confirmed SMS note sent OK.")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech confirmed note")

                    # Check if dispatch has a sms 12 hours note
                    if tech_12_hours_before_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_12:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 12h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS 12h note")
                        result_sms_12_sended = await self._send_tech_12_sms(dispatch_number, ticket_id, dispatch,
                                                                            sms_to)
                        if not result_sms_12_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS 12h not sended")
                            continue

                        result_append_tech_12_sms_note = await self._append_tech_12_sms_note(
                            dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_12_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 12 hours before note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 12 hours before note appended")
                        continue
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- Already has a sms tech 12 hours before note")

                    # Check if dispatch has a sms 2 hours note
                    if tech_2_hours_before_note_found is None:
                        just_now = datetime.now(pytz.utc)
                        hours_diff = UtilsRepository.get_diff_hours_between_datetimes(date_time_of_dispatch_localized,
                                                                                      just_now)
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} UTC - "
                                          f"dt: {date_time_of_dispatch_localized} - now: {just_now} - "
                                          f"diff: {hours_diff}")
                        if hours_diff > self.HOURS_2:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"SMS 2h note not needed to send now")
                            continue

                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"Sending SMS 2h note")
                        result_sms_2_sended = await self._send_tech_2_sms(dispatch_number, ticket_id, dispatch, sms_to)
                        if not result_sms_2_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS 2h not sended")
                            continue

                        result_append_tech_2_sms_note = await self._append_tech_2_sms_note(
                            dispatch_number, ticket_id, sms_to)
                        if not result_append_tech_2_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech 2 hours before note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech 2 hours before note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech 2 hours before note")

                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- This ticket should never be again in Dispatch Confirmed, "
                                      f"at some point it has to change to tech on site")

                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} - {dispatch}"
                    self._logger.error(f"Error: {ex}")
                    await self._notifications_repository.send_slack_message(err_msg)
                    continue
        except Exception as ex:
            err_msg = f"Error: _monitor_confirmed_dispatches - {ex}"
            self._logger.error(f"Error: {ex}")
            await self._notifications_repository.send_slack_message(err_msg)
        stop = perf_counter()
        self._logger.info(f"Monitor Confirmed Dispatches took: {(stop - start) / 60} minutes")

    async def _monitor_tech_on_site_dispatches(self, tech_on_site_dispatches):
        try:
            start = perf_counter()
            self._logger.info(f"Dispatches to process before filter {len(tech_on_site_dispatches)}")
            tech_on_site_dispatches = list(filter(self._is_tech_on_site, tech_on_site_dispatches))
            self._logger.info(f"Dispatches to process after filter {len(tech_on_site_dispatches)}")

            for dispatch in tech_on_site_dispatches:
                try:
                    dispatch_number = dispatch.get('Name', None)
                    ticket_id = dispatch.get('Ext_Ref_Num__c', None)

                    self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id}")
                    if ticket_id is None or not CtsRepository.is_valid_ticket_id(ticket_id) \
                            or dispatch_number is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} discarded.")
                        continue

                    date_time_of_dispatch = dispatch.get('Local_Site_Time__c')

                    if date_time_of_dispatch is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"Could not determine date time of dispatch: {dispatch}")
                        err_msg = f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"An error occurred retrieve datetime of dispatch: " \
                                  f"{dispatch.get('Local_Site_Time__c', None)}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    sms_to = CtsRepository.get_sms_to(dispatch)

                    if sms_to is None:
                        self._logger.info(f"Dispatch: [{dispatch_number}] for ticket_id: {ticket_id} "
                                          f"- Error: we could not retrieve 'sms_to' number from: "
                                          f"{dispatch.get('Description__c')}")
                        err_msg = f"An error occurred retrieve 'sms_to' number " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id} - " \
                                  f"from: {dispatch.get('Description__c')}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue

                    self._logger.info(f"Getting details for ticket [{ticket_id}]")

                    response = await self._bruin_repository.get_ticket_details(ticket_id)
                    response_status = response['status']
                    response_body = response['body']

                    if response_status not in range(200, 300):
                        self._logger.error(f"Error: Dispatch [{dispatch_number}] "
                                           f"Get ticket details for ticket {ticket_id}: "
                                           f"{response_body}")
                        err_msg = f"An error occurred retrieve getting ticket details from bruin " \
                                  f"Dispatch: {dispatch_number} - Ticket_id: {ticket_id}"
                        await self._notifications_repository.send_slack_message(err_msg)
                        continue
                    ticket_notes = response_body.get('ticketNotes', [])
                    ticket_notes = [tn for tn in ticket_notes if tn.get('noteValue')]

                    self._logger.info(
                        f"Checking watermarks for Dispatch [{dispatch_number}] in ticket_id: {ticket_id}")

                    self._logger.info(ticket_notes)

                    # watermark_found = UtilsRepository.find_note(ticket_notes, self.MAIN_WATERMARK)
                    requested_watermark_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_REQUESTED_WATERMARK)
                    confirmed_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_WATERMARK)
                    confirmed_sms_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_CONFIRMED_SMS_WATERMARK)
                    tech_12_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_12_HOURS_BEFORE_SMS_WATERMARK)
                    tech_2_hours_before_note_found = UtilsRepository.find_note(
                        ticket_notes, self.TECH_2_HOURS_BEFORE_SMS_WATERMARK)
                    tech_on_site_note_found = UtilsRepository.find_note(
                        ticket_notes, self.DISPATCH_FIELD_ENGINEER_ON_SITE_WATERMARK)
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"requested_watermark_found: {requested_watermark_found} "
                                      f"confirmed_note_found: {confirmed_note_found} "
                                      f"confirmed_sms_note_found: {confirmed_sms_note_found} "
                                      f"tech_12_hours_before_note_found: {tech_12_hours_before_note_found} "
                                      f"tech_2_hours_before_note_found: {tech_2_hours_before_note_found} "
                                      f"tech_on_site_note_found: {tech_on_site_note_found}")

                    # Check if dispatch was created by the dispatch portal
                    if requested_watermark_found is None:
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- Watermark not found, ticket does not belong to us")
                        continue
                    # TODO: check if we missed other notes?
                    if tech_on_site_note_found is None:
                        result_sms_tech_on_site_sended = await self._send_tech_on_site_sms(dispatch_number, ticket_id,
                                                                                           dispatch, sms_to)
                        if not result_sms_tech_on_site_sended:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- SMS tech on site not sended")
                            continue

                        result_append_tech_on_site_sms_note = await self._append_tech_on_site_sms_note(
                            dispatch_number, ticket_id, sms_to, dispatch.get('API_Resource_Name__c'))
                        if not result_append_tech_on_site_sms_note:
                            self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                              f"- A sms tech on site note not appended")
                            continue
                        self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                          f"- A sms tech on site note appended")
                    self._logger.info(f"Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "
                                      f"- already has a sms tech tech on site note")
                except Exception as ex:
                    err_msg = f"Error: Dispatch [{dispatch_number}] in ticket_id: {ticket_id} "\
                              f"- {dispatch}"
                    self._logger.error(err_msg)
                    await self._notifications_repository.send_slack_message(err_msg)
                    continue
        except Exception as ex:
            err_msg = f"Error: _monitor_tech_on_site_dispatches - {ex}"
            self._logger.error(f"Error: {ex}")
            await self._notifications_repository.send_slack_message(err_msg)

        stop = perf_counter()
        self._logger.info(f"Monitor Tech on Site Dispatches took: {(stop - start) / 60} minutes")
