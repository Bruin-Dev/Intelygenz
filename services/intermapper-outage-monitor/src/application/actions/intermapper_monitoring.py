import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone, utc
from pyzipcode import ZipCodeDatabase
from tenacity import retry, stop_after_delay, wait_exponential

from application import (
    AUTORESOLVE_REGEX,
    EVENT_REGEX,
    EVENT_TIME_REGEX,
    FORWARD_TICKET_TO_QUEUE_JOB_ID,
    REOPEN_NOTE_REGEX,
    TRIAGE_NOTE_REGEX,
    ZIP_CODE_REGEX,
    ForwardQueues,
)

logger = logging.getLogger(__name__)


class InterMapperMonitor:
    def __init__(
        self,
        scheduler,
        config,
        utils_repository,
        metrics_repository,
        notifications_repository,
        email_repository,
        bruin_repository,
        dri_repository,
    ):
        self._scheduler = scheduler
        self._config = config
        self._utils_repository = utils_repository
        self._metrics_repository = metrics_repository
        self._notifications_repository = notifications_repository
        self._email_repository = email_repository
        self._bruin_repository = bruin_repository
        self._dri_repository = dri_repository
        self._zip_db = ZipCodeDatabase()
        self._semaphore = asyncio.BoundedSemaphore(self._config.INTERMAPPER_CONFIG["concurrent_email_batches"])

    async def start_intermapper_outage_monitoring(self, exec_on_start=False):
        logger.info("Scheduling InterMapper Monitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            logger.info("InterMapper Monitor job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._intermapper_monitoring_process,
                "interval",
                seconds=self._config.INTERMAPPER_CONFIG["monitoring_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_intermapper_monitor_process",
            )
        except ConflictingIdError as conflict:
            logger.info(f"Skipping start of InterMapper Monitoring job. Reason: {conflict}")

    async def _intermapper_monitoring_process(self):
        logger.info(f'Processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}')
        start = time.time()
        unread_emails_response = await self._email_repository.get_unread_emails()
        unread_emails_body = unread_emails_response["body"]
        unread_emails_status = unread_emails_response["status"]

        if unread_emails_status not in range(200, 300):
            logger.warning(f"Bad status calling to get unread emails. Skipping intermapper monitoring process...")
            return

        emails_by_circuit_id = self._group_emails_by_circuit_id(unread_emails_body)
        tasks = [self._process_email_batch(emails, circuit_id) for circuit_id, emails in emails_by_circuit_id.items()]

        await asyncio.gather(*tasks)

        stop = time.time()
        logger.info(
            f'Finished processing unread emails from {self._config.INTERMAPPER_CONFIG["inbox_email"]}. '
            f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
        )

    def _group_emails_by_circuit_id(self, emails):
        emails_by_circuit_id = defaultdict(list)

        for email in emails:
            parsed_email_dict = self._parse_email_body(email["body"])
            circuit_id = self._extract_value_from_field("(", ")", parsed_email_dict["name"])
            emails_by_circuit_id[circuit_id].append(email)

        return emails_by_circuit_id

    async def _process_email_batch(self, emails, circuit_id):
        async with self._semaphore:
            logger.info(f"Processing {len(emails)} email(s) with circuit ID {circuit_id}...")

            if not circuit_id or circuit_id == "SD-WAN":
                for email in emails:
                    if self._config.CURRENT_ENVIRONMENT == "production":
                        await self._mark_email_as_read(email["msg_uid"])

                logger.info(f"Invalid circuit_id. Skipping emails with circuit_id {circuit_id}...")
                return

            response = await self._bruin_repository.get_service_number_by_circuit_id(circuit_id)
            response_status = response["status"]
            response_body = response["body"]

            if response_status not in range(200, 300):
                logger.error(
                    f"Failed to get service number by circuit ID. Skipping emails with circuit_id {circuit_id}..."
                )
                return

            if response_status == 204:
                logger.error(
                    f"Bruin returned a 204 when getting the service number for circuit_id {circuit_id}. "
                    f"Marking all emails with this circuit_id as read"
                )

                for email in emails:
                    if self._config.CURRENT_ENVIRONMENT == "production":
                        await self._mark_email_as_read(email["msg_uid"])

                return

            service_number = response_body["wtn"]
            client_id = response_body["clientID"]

            for email in emails:
                await self._process_email(email, service_number, client_id)

            logger.info(f"Finished processing all emails with circuit_id {circuit_id}!")

    async def _process_email(self, email, service_number, client_id):
        message = email["message"]
        body = email["body"]
        msg_uid = email["msg_uid"]
        subject = email["subject"]

        if message is None or msg_uid == -1:
            logger.error(f"Invalid message: {email}")
            return

        logger.info(f"Processing email with msg_uid: {msg_uid} and subject: {subject}")

        parsed_email_dict = self._parse_email_body(body)

        if parsed_email_dict["event"] in self._config.INTERMAPPER_CONFIG["intermapper_up_events"]:
            logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, there is no need to create '
                f"a new ticket. Checking for autoresolve ..."
            )
            event_processed_successfully = await self._autoresolve_ticket(service_number, client_id, parsed_email_dict)
        elif parsed_email_dict["event"] in self._config.INTERMAPPER_CONFIG["intermapper_down_events"]:
            logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, '
                f'condition was {parsed_email_dict["condition"]}. Checking for ticket creation ...'
            )
            dri_parameters = None
            if self._is_piab_device(parsed_email_dict):
                logger.info(
                    f"The probe type from Intermapper is {parsed_email_dict['probe_type']}."
                    f"Attempting to get additional parameters from DRI..."
                )
                dri_parameters = await self._get_dri_parameters(service_number, client_id)
            event_processed_successfully = await self._create_outage_ticket(
                service_number, client_id, parsed_email_dict, dri_parameters
            )
        else:
            logger.info(
                f'Event from InterMapper was {parsed_email_dict["event"]}, '
                f"so no further action is needs to be taken"
            )
            event_processed_successfully = True

        if event_processed_successfully and self._config.CURRENT_ENVIRONMENT == "production":
            await self._mark_email_as_read(msg_uid)

        if event_processed_successfully:
            logger.info(f"Processed email: {msg_uid}")
        else:
            logger.error(
                f"Email with msg_uid: {msg_uid} and subject: {subject} "
                f"related to service number: {service_number} could not be processed"
            )

    def _parse_email_body(self, body):
        parsed_email_dict = {}
        parsed_email_dict["time"] = EVENT_TIME_REGEX.match(body).group("time")
        parsed_email_dict["version"] = EVENT_TIME_REGEX.match(body).group("version")
        parsed_email_dict["event"] = self._find_field_in_body(body, "Event")
        parsed_email_dict["name"] = self._find_field_in_body(body, "Name")
        parsed_email_dict["document"] = self._find_field_in_body(body, "Document")
        parsed_email_dict["address"] = self._find_field_in_body(body, "Address")
        parsed_email_dict["probe_type"] = self._find_field_in_body(body, "Probe Type")
        parsed_email_dict["condition"] = self._find_field_in_body(body, "Condition", parsed_email_dict["event"])
        parsed_email_dict["previous_condition"] = self._find_field_in_body(body, "Previous Condition")
        parsed_email_dict["last_reported_down"] = self._find_field_in_body(body, "Time since last reported down")
        parsed_email_dict["up_time"] = self._find_field_in_body(body, "Device's up time")
        return parsed_email_dict

    def _find_field_in_body(self, email_body, field_name, default_value=""):
        email_body_lines = email_body.splitlines()
        field = None
        for line in email_body_lines:
            if line and len(line) > 0 and field_name in line:
                field = "".join(ch for ch in line)
                break
        if field is None or field.strip() == "":
            return None
        field_value = field.replace(f"{field_name}:", "").strip()
        return field_value or default_value

    def _extract_value_from_field(self, starting_char, ending_char, field):
        extracted_value = None
        if all(char in field for char in (starting_char, ending_char)):
            if starting_char == ending_char:
                extracted_value = field.split(starting_char)[1]
            else:
                extracted_value = field.split(starting_char)[1].split(ending_char)[0]
        return extracted_value

    async def _autoresolve_ticket(self, service_number, client_id, parsed_email_dict):
        is_piab = self._is_piab_device(parsed_email_dict)

        logger.info("Starting the autoresolve process")
        tickets_response = await self._bruin_repository.get_ticket_basic_info(client_id, service_number)
        tickets_body = tickets_response["body"]
        tickets_status = tickets_response["status"]
        if tickets_status not in range(200, 300):
            logger.warning(
                f"Bad status calling to get ticket basic info for client id:  {client_id}."
                f"Skipping autoresolve ticket ..."
            )
            return False
        logger.info(f"Found {len(tickets_body)} tickets for service number {service_number} from bruin: {tickets_body}")

        for ticket in tickets_body:

            ticket_id = ticket["ticketID"]

            logger.info(
                f"Posting InterMapper UP note to task of ticket id {ticket_id} "
                f"related to service number {service_number}..."
            )
            up_note_response = await self._bruin_repository.append_intermapper_up_note(
                ticket_id, service_number, parsed_email_dict, is_piab
            )
            if up_note_response["status"] not in range(200, 300):
                logger.warning(
                    f"Bad status calling to append intermapper note to ticket id: {ticket_id}."
                    f"Skipping autoresolve ticket ...."
                )
                return False

            product_category_response = await self._bruin_repository.get_tickets(client_id, ticket_id)
            product_category_response_body = product_category_response["body"]
            product_category_response_status = product_category_response["status"]
            if product_category_response_status not in range(200, 300):
                logger.warning(
                    f"Bad status calling to get ticket for client id: {client_id} and "
                    f"ticket id: {ticket_id}. Skipping autoresolve ticket ..."
                )
                return False

            if not product_category_response_body:
                logger.info(f"Ticket {ticket_id} couldn't be found in Bruin. Skipping autoresolve...")
                continue

            product_category = product_category_response_body[0].get("category")
            logger.info(f"Product category of ticket {ticket_id} from bruin is {product_category}")

            if self._are_all_product_categories_whitelisted(product_category) is False:
                logger.info(
                    f"At least one product category of ticket {ticket_id} from the "
                    f"following list is not one of the whitelisted categories for "
                    f"auto-resolve: {product_category}. Skipping autoresolve ..."
                )
                continue

            outage_ticket_creation_date = ticket["createDate"]

            logger.info(f"Checking to see if ticket {ticket_id} can be autoresolved")

            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
            ticket_details_body = ticket_details_response["body"]
            ticket_details_status = ticket_details_response["status"]
            if ticket_details_status not in range(200, 300):
                logger.warning(
                    f"Bad status calling get ticket details to ticket id: {ticket_id}. Skipping autoresolve ..."
                )
                return False

            details_from_ticket = ticket_details_body["ticketDetails"]
            detail_for_ticket_resolution = self._get_first_element_matching(
                details_from_ticket,
                lambda detail: detail["detailValue"] == service_number,
            )
            ticket_detail_id = detail_for_ticket_resolution["detailID"]

            notes_from_outage_ticket = ticket_details_body["ticketNotes"]
            relevant_notes = [
                note
                for note in notes_from_outage_ticket
                if note["serviceNumber"] is not None
                if service_number in note["serviceNumber"]
                if note["noteValue"] is not None
            ]

            if not self._was_last_outage_detected_recently(
                relevant_notes, outage_ticket_creation_date, parsed_email_dict
            ):
                logger.info(
                    f"Edge has been in outage state for a long time, so detail {ticket_detail_id} "
                    f"(service number {service_number}) of ticket {ticket_id} will not be autoresolved. Skipping "
                    f"autoresolve..."
                )
                continue

            can_detail_be_autoresolved_one_more_time = self._is_outage_ticket_detail_auto_resolvable(
                relevant_notes, service_number
            )
            if not can_detail_be_autoresolved_one_more_time:
                logger.info(
                    f"Limit to autoresolve detail {ticket_detail_id} (service number {service_number}) "
                    f"of ticket {ticket_id} has been maxed out already. "
                    "Skipping autoresolve..."
                )
                continue

            if self._is_detail_resolved(detail_for_ticket_resolution):
                logger.info(
                    f"Detail {ticket_detail_id} (service number {service_number}) of ticket {ticket_id} is already "
                    "resolved. Skipping autoresolve..."
                )
                continue

            if self._config.CURRENT_ENVIRONMENT != "production":
                logger.info(
                    f"Skipping autoresolve for service number {service_number} "
                    f"since the current environment is not production"
                )
                continue

            last_cycle_notes = self._get_notes_appended_since_latest_reopen_or_ticket_creation(relevant_notes)
            event = self._get_event_from_ticket_notes(last_cycle_notes)

            await self._bruin_repository.unpause_ticket_detail(
                ticket_id, service_number=service_number, detail_id=ticket_detail_id
            )

            resolve_ticket_response = await self._bruin_repository.resolve_ticket(ticket_id, ticket_detail_id)
            if resolve_ticket_response["status"] not in range(200, 300):
                logger.warning(f"Bad status calling to resolve ticket: {ticket_id}. Skipping autoresolve ...")
                return False

            logger.info(
                f"Autoresolve was successful for task of ticket {ticket_id} related to "
                f"service number {service_number}. Posting autoresolve note..."
            )
            self._metrics_repository.increment_tasks_autoresolved(event=event, is_piab=is_piab)
            await self._bruin_repository.append_autoresolve_note(ticket_id, service_number)
            slack_message = (
                f"Outage ticket {ticket_id} for service_number {service_number} was autoresolved through InterMapper "
                f"emails. Ticket details at https://app.bruin.com/t/{ticket_id}."
            )
            await self._notifications_repository.send_slack_message(slack_message)
            logger.info(
                f"Detail {ticket_detail_id} (service number {service_number}) of ticket {ticket_id} was autoresolved!"
            )

            self._remove_job_for_autoresolved_task(ForwardQueues.HNOC.value, ticket_id, service_number)
            self._remove_job_for_autoresolved_task(ForwardQueues.IPA.value, ticket_id, service_number)
        return True

    async def _create_outage_ticket(self, service_number, client_id, parsed_email_dict, dri_parameters):
        event = parsed_email_dict["event"]
        is_piab = self._is_piab_device(parsed_email_dict)

        logger.info(f"Attempting outage ticket creation for client_id {client_id} and service_number {service_number}")

        if self._config.CURRENT_ENVIRONMENT != "production":
            logger.info(
                f"No outage ticket will be created for client_id {client_id} and service_number {service_number} "
                f"since the current environment is not production"
            )
            return True

        outage_ticket_response = await self._bruin_repository.create_outage_ticket(client_id, service_number)
        outage_ticket_status = outage_ticket_response["status"]
        ticket_id = outage_ticket_response["body"]
        logger.info(f"Bruin response for ticket creation for service number {service_number}: {outage_ticket_response}")

        is_bruin_custom_status = outage_ticket_status in (409, 472, 473)

        if outage_ticket_status in range(200, 300):
            logger.info(f"Successfully created outage ticket with ticket_id {ticket_id}")
            self._metrics_repository.increment_tasks_created(event=event, is_piab=is_piab)
            slack_message = (
                f"Outage ticket created through InterMapper emails for service_number {service_number}. Ticket "
                f"details at https://app.bruin.com/t/{ticket_id}."
            )
            await self._notifications_repository.send_slack_message(slack_message)
        elif is_bruin_custom_status:
            logger.info(
                f"Ticket for service number {service_number} already exists with ticket_id {ticket_id}."
                f"Status returned was {outage_ticket_status}"
            )
            if outage_ticket_status == 409:
                logger.info(f"In Progress ticket exists for location of service number {service_number}")
            if outage_ticket_status == 472:
                logger.info(f"Resolved ticket exists for service number {service_number}")
                self._metrics_repository.increment_tasks_reopened(event=event, is_piab=is_piab)
            if outage_ticket_status == 473:
                logger.info(f"Resolved ticket exists for location of service number {service_number}")
                self._metrics_repository.increment_tasks_reopened(event=event, is_piab=is_piab)
        else:
            return False
        if dri_parameters:
            logger.info(f"Appending InterMapper note to ticket id {ticket_id} with dri parameters: {dri_parameters}")
            append_dri_note_response = await self._bruin_repository.append_dri_note(
                ticket_id, dri_parameters, parsed_email_dict
            )
            if append_dri_note_response["status"] not in range(200, 300):
                logger.warning(f"Bad status calling append dri note. Skipping create outage ticket ...")
                return False
            return True
        logger.info(f"Appending InterMapper note to ticket id {ticket_id}")
        append_intermapper_note_response = await self._bruin_repository.append_intermapper_note(
            ticket_id, parsed_email_dict, self._is_piab_device(parsed_email_dict)
        )
        if append_intermapper_note_response["status"] not in range(200, 300):
            logger.warning(f"Bad status calling append intermapper note. Skipping create outage ticket ...")
            return False

        if self._should_forward_to_ipa_queue(parsed_email_dict) and outage_ticket_status in (200, 471, 472, 473):
            ipa_forward_time = self._config.INTERMAPPER_CONFIG["forward_to_ipa_job_interval"]
            self._schedule_forward_to_queue(
                ticket_id, service_number, ForwardQueues.IPA.value, ipa_forward_time, is_piab, event
            )

            hnoc_forward_time = self._config.INTERMAPPER_CONFIG["forward_to_hnoc_job_interval"]
            self._schedule_forward_to_queue(
                ticket_id, service_number, ForwardQueues.HNOC.value, hnoc_forward_time, is_piab, event
            )
        return True

    async def _get_dri_parameters(self, service_number, client_id):
        attributes_serial_response = await self._bruin_repository.get_serial_attribute_from_inventory(
            service_number,
            client_id,
        )
        if attributes_serial_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status while getting inventory attributes' serial number for service number {service_number} "
                f"and client ID {client_id}. Skipping get DRI parameters..."
            )
            return None

        attributes_serial = attributes_serial_response["body"]
        if attributes_serial is None:
            logger.warning(
                f"No inventory attributes' found for service number {service_number} and client ID {client_id}. "
                "Skipping get DRI parameters..."
            )
            return None

        dri_parameters_response = await self._dri_repository.get_dri_parameters(attributes_serial)
        if dri_parameters_response["status"] not in range(200, 300):
            logger.warning(
                f"Bad status while getting DRI parameters based on inventory attributes' serial number "
                f"{attributes_serial} for service number {service_number} and client ID {client_id}. "
                f"Skipping get DRI parameters..."
            )
            return None

        return dri_parameters_response["body"]

    def _was_last_outage_detected_recently(
        self, ticket_notes: list, ticket_creation_date: str, parsed_email_dict: dict
    ) -> bool:
        tz_offset = self._get_tz_offset(parsed_email_dict["name"])
        max_seconds_since_last_outage = self._get_max_seconds_since_last_outage(tz_offset)

        current_datetime = datetime.now(utc)
        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note["createdDate"])

        last_reopen_note = self._get_last_element_matching(
            notes_sorted_by_date_asc, lambda note: REOPEN_NOTE_REGEX.match(note["noteValue"])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note["createdDate"]).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        triage_note = self._get_last_element_matching(
            notes_sorted_by_date_asc, lambda note: TRIAGE_NOTE_REGEX.match(note["noteValue"])
        )
        if triage_note:
            note_creation_date = parse(triage_note["createdDate"]).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_outage = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

    def _is_outage_ticket_detail_auto_resolvable(self, ticket_notes: list, serial_number: str) -> bool:
        max_autoresolves = self._config.INTERMAPPER_CONFIG["autoresolve"]["max_autoresolves"]
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note["noteValue"]
            is_autoresolve_note = bool(AUTORESOLVE_REGEX.match(note_value))
            is_note_related_to_serial = serial_number in ticket_note["serviceNumber"]
            times_autoresolved += int(is_autoresolve_note and is_note_related_to_serial)

            if times_autoresolved >= max_autoresolves:
                return False

        return True

    async def _mark_email_as_read(self, msg_uid):
        mark_email_as_read_response = await self._email_repository.mark_email_as_read(msg_uid)
        mark_email_as_read_status = mark_email_as_read_response["status"]

        if mark_email_as_read_status not in range(200, 300):
            logger.error(f"Could not mark email with msg_uid: {msg_uid} as read")

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
            if product_category not in self._config.INTERMAPPER_CONFIG["autoresolve"]["product_category_list"]:
                return False
        return True

    @staticmethod
    def _is_piab_device(email_data: dict) -> bool:
        return "Data Remote Probe" in email_data["probe_type"]

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail["detailStatus"] == "R"

    def _get_tz_offset(self, name):
        try:
            zip_code = ZIP_CODE_REGEX.search(name).group("zip_code")
            tz_offset = self._zip_db.get(zip_code).timezone
        except Exception:
            tz_offset = self._get_offset_from_tz_name(self._config.TIMEZONE)

        return tz_offset

    @staticmethod
    def _get_offset_from_tz_name(tz_name):
        tz = timezone(tz_name)
        tz_offset = datetime.now(tz).strftime("%z")
        return int(tz_offset[0:3])

    def _get_max_seconds_since_last_outage(self, tz_offset: int) -> int:
        from datetime import timezone

        tz = timezone(timedelta(hours=tz_offset))
        now = datetime.now(tz=tz)

        last_outage_seconds = self._config.INTERMAPPER_CONFIG["autoresolve"]["last_outage_seconds"]
        day_schedule = self._config.INTERMAPPER_CONFIG["autoresolve"]["day_schedule"]
        day_start_hour = day_schedule["start_hour"]
        day_end_hour = day_schedule["end_hour"]

        if day_start_hour >= day_end_hour:
            day_end_hour += 24

        if day_start_hour <= now.hour < day_end_hour:
            return last_outage_seconds["day"]
        else:
            return last_outage_seconds["night"]

    def _get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        sorted_ticket_notes = sorted(ticket_notes, key=lambda note: note["createdDate"])
        latest_reopen = self._utils_repository.get_last_element_matching(
            sorted_ticket_notes, lambda note: REOPEN_NOTE_REGEX.search(note["noteValue"])
        )

        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last outage
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    @staticmethod
    def _get_event_from_ticket_notes(ticket_notes: List[dict]) -> Optional[str]:
        for note in ticket_notes:
            match = EVENT_REGEX.search(note["noteValue"])
            if match:
                return match.group("event")

    def _is_battery_alert_probe_type(self, probe_type: str) -> bool:
        battery_alert_probe_types = self._config.INTERMAPPER_CONFIG["battery_alert_probe_types"]
        return any(pt for pt in battery_alert_probe_types if pt in probe_type)

    def _is_battery_alert_condition(self, probe_condition: str) -> bool:
        battery_alert_probe_conditions = self._config.INTERMAPPER_CONFIG["battery_alert_probe_conditions"]
        return any(pc for pc in battery_alert_probe_conditions if pc == probe_condition)

    def _should_forward_to_ipa_queue(self, parsed_email_dict: Dict[str, str]) -> bool:
        return self._is_battery_alert_probe_type(parsed_email_dict["probe_type"]) and self._is_battery_alert_condition(
            parsed_email_dict["condition"]
        )

    def _schedule_forward_to_queue(
        self,
        ticket_id: int,
        serial_number: str,
        target_queue: str,
        forward_time: float,
        is_piab: bool,
        event: str,
    ):
        tz = timezone(self._config.TIMEZONE)
        current_datetime = datetime.now(tz)
        forward_task_run_date = current_datetime + timedelta(seconds=forward_time)

        logger.info(
            f"Scheduling {target_queue} queue forwarding for ticket_id {ticket_id} and service number {serial_number}"
            f" to happen at timestamp: {forward_task_run_date}"
        )

        _target_queue = target_queue.replace(" ", "_")
        job_id = FORWARD_TICKET_TO_QUEUE_JOB_ID.format(
            ticket_id=ticket_id, serial_number=serial_number, target_queue=_target_queue
        )
        self._scheduler.add_job(
            self.forward_ticket_to_queue,
            "date",
            kwargs={
                "ticket_id": ticket_id,
                "serial_number": serial_number,
                "target_queue": target_queue,
                "is_piab": is_piab,
                "event": event,
            },
            run_date=forward_task_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            coalesce=True,
            id=job_id,
        )

    async def forward_ticket_to_queue(
        self,
        ticket_id: int,
        serial_number: str,
        target_queue: str,
        is_piab: bool,
        event: str,
    ):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.NATS_CONFIG["multiplier"], min=self._config.NATS_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.NATS_CONFIG["stop_delay"]),
        )
        async def forward_ticket_to_queue():
            logger.info(
                f"Checking if ticket_id {ticket_id} for serial {serial_number} is resolved before "
                f"attempting to forward to {target_queue} queue..."
            )

            await self.change_detail_work_queue(
                ticket_id=ticket_id,
                serial_number=serial_number,
                target_queue=target_queue,
                is_piab=is_piab,
                event=event,
            )

        try:
            await forward_ticket_to_queue()
        except Exception as e:
            logger.error(
                f"An error occurred while trying to forward ticket_id {ticket_id} for serial {serial_number} to"
                f" {target_queue} queue -> {e}"
            )

    async def change_detail_work_queue(
        self, ticket_id: int, serial_number: str, target_queue: str, is_piab: bool, event: str
    ):
        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            serial_number=serial_number, ticket_id=ticket_id, task_result=target_queue
        )

        if change_detail_work_queue_response["status"] in range(200, 300):
            logger.info(
                f"Successfully forwarded ticket_id {ticket_id} and serial {serial_number} to {target_queue} queue."
            )
            self._metrics_repository.increment_tasks_forwarded(event=event, is_piab=is_piab, target_queue=target_queue)

            slack_message = (
                f"Detail of ticket {ticket_id} related to serial {serial_number} was successfully forwarded "
                f"to {target_queue} queue!"
            )
            await self._notifications_repository.send_slack_message(slack_message)

            if target_queue == ForwardQueues.HNOC.value:
                email_response = await self._bruin_repository.send_forward_email_milestone_notification(
                    ticket_id, serial_number
                )
                if email_response["status"] not in range(200, 300):
                    logger.error(
                        f"Forward email related to service number {serial_number} could not be sent for ticket "
                        f"{ticket_id}!"
                    )
        else:
            logger.error(
                f"Failed to forward ticket_id {ticket_id} and "
                f"serial {serial_number} to {target_queue} queue due to bruin "
                f"returning {change_detail_work_queue_response} when attempting to forward to {target_queue} queue."
            )

    def _remove_job_for_autoresolved_task(self, target_queue: str, ticket_id: int, serial_number: str):
        _target_queue = target_queue.replace(" ", "_")
        job_id = FORWARD_TICKET_TO_QUEUE_JOB_ID.format(
            ticket_id=ticket_id, serial_number=serial_number, target_queue=_target_queue
        )
        if self._scheduler.get_job(job_id):
            logger.info(
                f"Found job to forward to {target_queue} scheduled for autoresolved ticket {ticket_id}"
                f" related to serial number {serial_number}! Removing..."
            )
            self._scheduler.remove_job(job_id)
