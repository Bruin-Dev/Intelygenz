import re
import time
from datetime import datetime
from typing import Callable

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc

TRIAGE_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nInterMapper Triage")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nRe-opening")


class InterMapperMonitor:
    def __init__(self, event_bus, logger, scheduler, config, notifications_repository, bruin_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository

    async def start_intermapper_outage_monitoring(self, exec_on_start=False):
        self._logger.info('Scheduling InterMapper Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.INTERMAPPER_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('InterMapper Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._intermapper_monitoring_process, 'interval',
                                    seconds=self._config.INTERMAPPER_CONFIG['monitoring_interval'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_intermapper_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of InterMapper Monitoring job. Reason: {conflict}')

    async def _intermapper_monitoring_process(self):
        self._logger.info(f'Processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}')
        start = time.time()
        unread_emails_response = await self._notifications_repository.get_unread_emails()
        unread_emails_body = unread_emails_response['body']
        unread_emails_status = unread_emails_response['status']
        if unread_emails_status not in range(200, 300):
            return
        for email in unread_emails_body:
            message = email['message']
            body = email['body']
            msg_uid = email['msg_uid']
            if message is None or msg_uid == -1:
                self._logger.error(f'Invalid message: {email}')
                continue
            email_subject = email['subject']

            self._logger.info(f'Processing email with msg_uid: {msg_uid} and subject: {email_subject}')

            parsed_email_dict = self._parse_email_body(body)

            self._logger.info('Grabbing the asset_id from the InterMapper email')
            asset_id = self._extract_value_from_field('(', ')', parsed_email_dict['name'])

            if asset_id is None or asset_id == 'SD-WAN':
                mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
                mark_email_as_read_status = mark_email_as_read_response['status']
                if mark_email_as_read_status not in range(200, 300):
                    self._logger.error(f'Could not mark email with msg_uid: {msg_uid} and '
                                       f'subject: {email_subject} as read')
                continue

            circuit_id_response = await self._bruin_repository.get_circuit_id(asset_id)
            circuit_id_status = circuit_id_response['status']
            if circuit_id_status not in range(200, 300):
                continue
            if circuit_id_status == 204:
                self._logger.error(f'Bruin returned a 204 when getting the circuit id of asset_id {asset_id}.'
                                   f'Marking email as read')
                mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
                mark_email_as_read_status = mark_email_as_read_response['status']
                if mark_email_as_read_status not in range(200, 300):
                    self._logger.error(f'Could not mark email with msg_uid: {msg_uid} and '
                                       f'subject: {email_subject} as read')
                continue
            circuit_id_body = circuit_id_response['body']
            circuit_id = circuit_id_body['wtn']
            self._logger.info(f'Got circuit_id from bruin: {circuit_id}')

            self._logger.info('Grabbing the client_id from bruin ')
            client_id = circuit_id_body['clientID']
            self._logger.info(f'Got client_id {client_id} from bruin')
            event_processed_successfully = False
            if parsed_email_dict['event'] in self._config.INTERMAPPER_CONFIG['intermapper_up_events']:
                self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]} there is no need to create'
                                  f' a new ticket. Checking for autoresolve ...')
                event_processed_successfully = await self._autoresolve_ticket(circuit_id, client_id, body)
            elif parsed_email_dict['event'] in self._config.INTERMAPPER_CONFIG['intermapper_down_events']:
                self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]}, '
                                  f'checking for ticket creation ...')
                event_processed_successfully = await self._create_outage_ticket(circuit_id, client_id, body)
            else:
                self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]}, '
                                  f'so no further action is needs to be taken')
                event_processed_successfully = True

            if event_processed_successfully is True:
                mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
                mark_email_as_read_status = mark_email_as_read_response['status']
                if mark_email_as_read_status not in range(200, 300):
                    self._logger.error(f'Could not mark email with msg_uid: {msg_uid} and '
                                       f'subject: {email_subject} as read')
                self._logger.info(f'Processed email: {msg_uid}')
            else:
                self._logger.info(f'An error occurred when doing the process related the event. Skipping the process'
                                  f'to mark email with msg_uid: {msg_uid} and subject: {email_subject} as read')

        stop = time.time()
        self._logger.info(f'Finished processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}'
                          f'Elapsed time:{round((stop - start) / 60, 2)} minutes')

    def _parse_email_body(self, body):
        parsed_email_dict = {}
        parsed_email_dict['event'] = self._find_field_in_body(body, 'Event')
        parsed_email_dict['name'] = self._find_field_in_body(body, 'Name')
        parsed_email_dict['document'] = self._find_field_in_body(body, 'Document')
        parsed_email_dict['address'] = self._find_field_in_body(body, 'Address')
        parsed_email_dict['probe_type'] = self._find_field_in_body(body, 'Probe Type')
        parsed_email_dict['condition'] = self._find_field_in_body(body, 'Condition')
        parsed_email_dict['last_reported_down'] = self._find_field_in_body(body, 'Time since last reported down')
        parsed_email_dict['up_time'] = self._find_field_in_body(body, "Device's up time")
        return parsed_email_dict

    def _find_field_in_body(self, email_body, field_name):
        email_body_lines = email_body.splitlines()
        field = None
        for line in email_body_lines:
            if line and len(line) > 0 and field_name in line:
                field = ''.join(ch for ch in line)
                break
        if field is None or field.strip() == '':
            return None
        return field.strip().replace(f'{field_name}: ', '')

    def _extract_value_from_field(self, starting_char, ending_char, field):
        extracted_value = None
        if all(char in field for char in (starting_char, ending_char)):
            if starting_char == ending_char:
                extracted_value = field.split(starting_char)[1]
            else:
                extracted_value = field.split(starting_char)[1].split(ending_char)[0]
        return extracted_value

    async def _autoresolve_ticket(self, circuit_id, client_id, intermapper_body):
        self._logger.info('Starting the autoresolve process')
        tickets_response = await self._bruin_repository.get_ticket_basic_info(client_id, circuit_id)
        tickets_body = tickets_response['body']
        tickets_status = tickets_response['status']
        if tickets_status not in range(200, 300):
            return False
        self._logger.info(f'Found {len(tickets_body)} tickets for circuit ID {circuit_id} from bruin:')
        self._logger.info(tickets_body)

        for ticket in tickets_body:

            ticket_id = ticket['ticketID']

            product_category_response = await self._bruin_repository.get_tickets(client_id, ticket_id)
            product_category_response_body = product_category_response['body']
            product_category_response_status = product_category_response['status']
            if product_category_response_status not in range(200, 300):
                return False

            if not product_category_response_body:
                self._logger.info(f"Ticket {ticket_id} couldn't be found in Bruin. Skipping autoresolve...")
                continue

            product_category = product_category_response_body[0].get('category')

            self._logger.info(f'Product category of ticket {ticket_id} is {product_category}')

            if product_category not in self._config.INTERMAPPER_CONFIG['autoresolve_product_category_list']:
                self._logger.info(f"Product category of ticket {ticket_id} is {product_category}, and is not "
                                  f"one of the categories we autoresolve for. Skipping autoresolve ...")
                continue

            outage_ticket_creation_date = ticket['createDate']

            self._logger.info(f'Checking to see if ticket {ticket_id} can be autoresolved')

            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
            ticket_details_body = ticket_details_response['body']
            ticket_details_status = ticket_details_response['status']
            if ticket_details_status not in range(200, 300):
                return False

            details_from_ticket = ticket_details_body['ticketDetails']
            detail_for_ticket_resolution = self._get_first_element_matching(
                details_from_ticket,
                lambda detail: detail['detailValue'] == circuit_id,
            )
            ticket_detail_id = detail_for_ticket_resolution['detailID']

            notes_from_outage_ticket = ticket_details_body['ticketNotes']
            relevant_notes = [
                note
                for note in notes_from_outage_ticket
                if circuit_id in note['serviceNumber']
                if note['noteValue'] is not None
            ]

            if not self._was_last_outage_detected_recently(relevant_notes, outage_ticket_creation_date):
                self._logger.info(
                    f'Edge has been in outage state for a long time, so detail {ticket_detail_id} '
                    f'(circuit ID {circuit_id}) of ticket {ticket_id} will not be autoresolved. Skipping '
                    f'autoresolve...'
                )
                continue

            can_detail_be_autoresolved_one_more_time = self._is_outage_ticket_detail_auto_resolvable(
                relevant_notes, circuit_id, max_autoresolves=3
            )
            if not can_detail_be_autoresolved_one_more_time:
                self._logger.info(
                    f'Limit to autoresolve detail {ticket_detail_id} (circuit ID {circuit_id}) '
                    f'of ticket {ticket_id} has been maxed out already. '
                    'Skipping autoresolve...'
                )
                continue
            resolve_ticket_response = await self._bruin_repository.resolve_ticket(ticket_id, ticket_detail_id)
            if resolve_ticket_response['status'] not in range(200, 300):
                return False

            await self._bruin_repository.append_autoresolve_note(ticket_id, circuit_id, intermapper_body)
            slack_message = (
                f'Outage ticket {ticket_id} for circuit_id {circuit_id} was autoresolved through InterMapper emails. '
                f'Ticket details at https://app.bruin.com/t/{ticket_id}.'
            )
            await self._notifications_repository.send_slack_message(slack_message)
            self._logger.info(
                f'Detail {ticket_detail_id} (circuit ID {circuit_id}) of ticket {ticket_id} '
                f'was autoresolved!'
            )
        return True

    async def _create_outage_ticket(self, circuit_id, client_id, intermapper_body):
        self._logger.info(f'Attempting outage ticket creation for client_id {client_id}, '
                          f'and circuit_id {circuit_id}')
        outage_ticket_response = await self._bruin_repository.create_outage_ticket(client_id, circuit_id)
        outage_ticket_status = outage_ticket_response['status']
        outage_ticket_body = outage_ticket_response['body']
        self._logger.info(f"Bruin response for ticket creation for edge with circuit id {circuit_id}: "
                          f"{outage_ticket_response}")

        is_bruin_custom_status = outage_ticket_status in (409, 472, 473)

        if outage_ticket_status in range(200, 300):
            self._logger.info(f'Successfully created outage ticket with ticket_id {outage_ticket_body}')
            slack_message = (
                f'Outage ticket created through InterMapper emails for circuit_id {circuit_id}. Ticket '
                f'details at https://app.bruin.com/t/{outage_ticket_body}.'
            )
            await self._notifications_repository.send_slack_message(slack_message)
        elif is_bruin_custom_status:
            self._logger.info(f'Ticket for circuit id {circuit_id} already exists with ticket_id {outage_ticket_body}.'
                              f'Status returned was {outage_ticket_status}')
            if outage_ticket_status == 409:
                self._logger.info(f'In Progress ticket exists for location of circuit id {circuit_id}')
            if outage_ticket_status == 472:
                self._logger.info(f'Resolved ticket exists for circuit id {circuit_id}')
            if outage_ticket_status == 473:
                self._logger.info(f'Resolved ticket exists for location of circuit id {circuit_id}')
        else:
            return False

        self._logger.info(f'Appending InterMapper note to ticket id {outage_ticket_body}')
        await self._bruin_repository.append_intermapper_note(outage_ticket_body, intermapper_body)
        return True

    def _was_last_outage_detected_recently(self, ticket_notes: list, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_outage = self._config.INTERMAPPER_CONFIG['autoresolve_last_outage_seconds']

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])

        last_reopen_note = self._get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.match(note['noteValue'])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        triage_note = self._get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: TRIAGE_NOTE_REGEX.match(note['noteValue'])
        )
        if triage_note:
            note_creation_date = parse(triage_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_outage = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

    def _is_outage_ticket_detail_auto_resolvable(self, ticket_notes: list,
                                                 serial_number: str,
                                                 max_autoresolves: int) -> bool:
        regex = re.compile(r"^#\*(MetTel's IPA)\*#\nAuto-resolving task for")
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note['noteValue']
            is_autoresolve_note = bool(regex.match(note_value))
            is_note_related_to_serial = serial_number in ticket_note['serviceNumber']
            times_autoresolved += int(is_autoresolve_note and is_note_related_to_serial)

            if times_autoresolved >= max_autoresolves:
                return False

        return True

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def _get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self._get_first_element_matching(reversed(iterable), condition, fallback)
