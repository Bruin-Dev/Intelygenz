import asyncio
import re
import time
from datetime import datetime
from collections import defaultdict
from typing import Callable

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc

TRIAGE_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nInterMapper Triage")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nRe-opening")
EVENT_TIME_REGEX = re.compile(r'(?P<time>^.*): Message from InterMapper')


class InterMapperMonitor:
    def __init__(self, event_bus, logger, scheduler, config, notifications_repository, bruin_repository,
                 dri_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._notifications_repository = notifications_repository
        self._bruin_repository = bruin_repository
        self._dri_repository = dri_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.INTERMAPPER_CONFIG['concurrent_email_batches'])

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

        emails_by_asset_id = self._group_emails_by_asset_id(unread_emails_body)
        tasks = [self._process_email_batch(emails, asset_id) for asset_id, emails in emails_by_asset_id.items()]

        await asyncio.gather(*tasks)

        stop = time.time()
        self._logger.info(f'Finished processing unread emails from {self._config.INTERMAPPER_CONFIG["inbox_email"]}. '
                          f'Elapsed time: {round((stop - start) / 60, 2)} minutes')

    def _group_emails_by_asset_id(self, emails):
        emails_by_asset_id = defaultdict(list)

        for email in emails:
            parsed_email_dict = self._parse_email_body(email['body'])
            asset_id = self._extract_value_from_field('(', ')', parsed_email_dict['name'])
            emails_by_asset_id[asset_id].append(email)

        return emails_by_asset_id

    async def _process_email_batch(self, emails, asset_id):
        async with self._semaphore:
            self._logger.info(f'Processing {len(emails)} email(s) with asset_id {asset_id}...')

            if not asset_id or asset_id == 'SD-WAN':
                for email in emails:
                    await self._mark_email_as_read(email['msg_uid'])

                self._logger.info(f'Invalid asset_id. Skipping emails with asset_id {asset_id}...')
                return

            circuit_id_response = await self._bruin_repository.get_circuit_id(asset_id)
            circuit_id_status = circuit_id_response['status']
            circuit_id_body = circuit_id_response['body']

            if circuit_id_status not in range(200, 300):
                self._logger.error(f'Failed to get circuit id. Skipping emails with asset_id {asset_id}...')
                return

            if circuit_id_status == 204:
                self._logger.error(f'Bruin returned a 204 when getting the circuit id of asset_id {asset_id}. '
                                   f'Marking all emails with this asset_id as read')

                for email in emails:
                    await self._mark_email_as_read(email['msg_uid'])

                return

            circuit_id = circuit_id_body['wtn']
            client_id = circuit_id_body['clientID']

            for email in emails:
                await self._process_email(email, circuit_id, client_id)

            self._logger.info(f'Finished processing all emails with asset_id {asset_id}!')

    async def _process_email(self, email, circuit_id, client_id):
        message = email['message']
        body = email['body']
        msg_uid = email['msg_uid']
        subject = email['subject']

        if message is None or msg_uid == -1:
            self._logger.error(f'Invalid message: {email}')
            return

        self._logger.info(f'Processing email with msg_uid: {msg_uid} and subject: {subject}')

        parsed_email_dict = self._parse_email_body(body)

        if parsed_email_dict['event'] in self._config.INTERMAPPER_CONFIG['intermapper_up_events']:
            self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]} there is no need to create'
                              f' a new ticket. Checking for autoresolve ...')
            event_processed_successfully = await self._autoresolve_ticket(circuit_id, client_id, parsed_email_dict)
        elif parsed_email_dict['event'] in self._config.INTERMAPPER_CONFIG['intermapper_down_events']:
            self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]}, '
                              f'checking for ticket creation ...')
            dri_parameters = None
            if self._is_piab_device(parsed_email_dict):
                self._logger.info(f"The probe type from Intermapper is {parsed_email_dict['probe_type']}."
                                  f"Attempting to get additional parameters from DRI...")
                dri_parameters = await self._get_dri_parameters(circuit_id, client_id)
            event_processed_successfully = await self._create_outage_ticket(circuit_id, client_id, parsed_email_dict,
                                                                            dri_parameters)
        else:
            self._logger.info(f'Event from InterMapper was {parsed_email_dict["event"]}, '
                              f'so no further action is needs to be taken')
            event_processed_successfully = True

        if event_processed_successfully:
            await self._mark_email_as_read(msg_uid)
            self._logger.info(f'Processed email: {msg_uid}')
        else:
            self._logger.error(f'Email with msg_uid: {msg_uid} and subject: {subject} '
                               f'related to circuit ID: {circuit_id} could not be processed')

    def _parse_email_body(self, body):
        parsed_email_dict = {}
        parsed_email_dict['time'] = EVENT_TIME_REGEX.match(body).group('time')
        parsed_email_dict['event'] = self._find_field_in_body(body, 'Event')
        parsed_email_dict['name'] = self._find_field_in_body(body, 'Name')
        parsed_email_dict['document'] = self._find_field_in_body(body, 'Document')
        parsed_email_dict['address'] = self._find_field_in_body(body, 'Address')
        parsed_email_dict['probe_type'] = self._find_field_in_body(body, 'Probe Type')
        parsed_email_dict['condition'] = self._find_field_in_body(body, 'Condition', parsed_email_dict['event'])
        parsed_email_dict['previous_condition'] = self._find_field_in_body(body, 'Previous Condition')
        parsed_email_dict['last_reported_down'] = self._find_field_in_body(body, 'Time since last reported down')
        parsed_email_dict['up_time'] = self._find_field_in_body(body, "Device's up time")
        return parsed_email_dict

    def _find_field_in_body(self, email_body, field_name, default_value=''):
        email_body_lines = email_body.splitlines()
        field = None
        for line in email_body_lines:
            if line and len(line) > 0 and field_name in line:
                field = ''.join(ch for ch in line)
                break
        if field is None or field.strip() == '':
            return None
        field_value = field.replace(f'{field_name}:', '').strip()
        return field_value or default_value

    def _extract_value_from_field(self, starting_char, ending_char, field):
        extracted_value = None
        if all(char in field for char in (starting_char, ending_char)):
            if starting_char == ending_char:
                extracted_value = field.split(starting_char)[1]
            else:
                extracted_value = field.split(starting_char)[1].split(ending_char)[0]
        return extracted_value

    async def _autoresolve_ticket(self, circuit_id, client_id, parsed_email_dict):
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

            self._logger.info(f'Posting InterMapper UP note to task of ticket id {ticket_id} '
                              f'related to circuit ID {circuit_id}...')
            up_note_response = await self._bruin_repository.append_intermapper_up_note(ticket_id, circuit_id,
                                                                                       parsed_email_dict)
            if up_note_response['status'] not in range(200, 300):
                return False

            product_category_response = await self._bruin_repository.get_tickets(client_id, ticket_id)
            product_category_response_body = product_category_response['body']
            product_category_response_status = product_category_response['status']
            if product_category_response_status not in range(200, 300):
                return False

            if not product_category_response_body:
                self._logger.info(f"Ticket {ticket_id} couldn't be found in Bruin. Skipping autoresolve...")
                continue

            product_category = product_category_response_body[0].get('category')
            self._logger.info(f'Product category of ticket {ticket_id} from bruin is {product_category}')

            if self._are_all_product_categories_whitelisted(product_category) is False:
                self._logger.info(f"At least one product category of ticket {ticket_id} from the "
                                  f"following list is not one of the whitelisted categories for "
                                  f"auto-resolve: {product_category}. Skipping autoresolve ...")
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

            self._logger.info(f'Autoresolve was successful for task of ticket {ticket_id} related to '
                              f'circuit ID {circuit_id}. Posting autoresolve note...')
            await self._bruin_repository.append_autoresolve_note(ticket_id, circuit_id)
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

    async def _create_outage_ticket(self, circuit_id, client_id, parsed_email_dict, dri_parameters):
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
        if dri_parameters:
            self._logger.info(f'Appending InterMapper note to ticket id {outage_ticket_body} with dri parameters: '
                              f'{dri_parameters}')
            append_dri_note_response = await self._bruin_repository.append_dri_note(outage_ticket_body, dri_parameters,
                                                                                    parsed_email_dict)
            if append_dri_note_response["status"] not in range(200, 300):
                return False
            return True
        self._logger.info(f'Appending InterMapper note to ticket id {outage_ticket_body}')
        append_intermapper_note_response = await self._bruin_repository.append_intermapper_note(outage_ticket_body,
                                                                                                parsed_email_dict)
        if append_intermapper_note_response["status"] not in range(200, 300):
            return False
        return True

    async def _get_dri_parameters(self, circuit_id, client_id):
        attributes_serial_response = await self._bruin_repository.get_attributes_serial(circuit_id, client_id)
        if attributes_serial_response["status"] not in range(200, 300):
            return None
        attributes_serial = attributes_serial_response["body"]
        dri_parameters_response = await self._dri_repository.get_dri_parameters(attributes_serial)
        if dri_parameters_response["status"] not in range(200, 300):
            return None
        return dri_parameters_response["body"]

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

    async def _mark_email_as_read(self, msg_uid):
        mark_email_as_read_response = await self._notifications_repository.mark_email_as_read(msg_uid)
        mark_email_as_read_status = mark_email_as_read_response['status']

        if mark_email_as_read_status not in range(200, 300):
            self._logger.error(f'Could not mark email with msg_uid: {msg_uid} as read')

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    def _get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self._get_first_element_matching(reversed(iterable), condition, fallback)

    def _are_all_product_categories_whitelisted(self, bruin_product_category: str) -> bool:
        all_product_categories = bruin_product_category.split(",")
        for product_category in all_product_categories:
            if product_category not in self._config.INTERMAPPER_CONFIG['autoresolve_product_category_list']:
                return False
        return True

    @staticmethod
    def _is_piab_device(email_data: dict) -> bool:
        return 'Data Remote Probe' in email_data['probe_type']
