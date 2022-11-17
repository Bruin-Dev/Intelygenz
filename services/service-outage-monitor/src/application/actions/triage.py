import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Set

from application import TRIAGE_NOTE_REGEX
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone, utc
from tenacity import retry, stop_after_delay, wait_exponential

logger = logging.getLogger(__name__)


class Triage:
    def __init__(
        self,
        scheduler,
        config,
        outage_repository,
        customer_cache_repository,
        bruin_repository,
        velocloud_repository,
        notifications_repository,
        triage_repository,
        ha_repository,
    ):
        self._scheduler = scheduler
        self._config = config
        self._outage_repository = outage_repository
        self._customer_cache_repository = customer_cache_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._ha_repository = ha_repository
        self._edges_status_by_serial = {}
        self._cached_info_by_serial = {}
        self.__reset_customer_cache()
        self._semaphore = asyncio.BoundedSemaphore(self._config.TRIAGE_CONFIG["semaphore"])

    def __reset_customer_cache(self):
        self._customer_cache = []

    async def start_triage_job(self, exec_on_start=False):
        logger.info(
            f"Scheduled task: service outage triage configured to run every "
            f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes'
        )
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            logger.info(f"It will be executed now")
        self._scheduler.add_job(
            self._run_tickets_polling,
            "interval",
            minutes=self._config.TRIAGE_CONFIG["polling_minutes"],
            next_run_time=next_run_time,
            replace_existing=True,
            id="_triage_process",
        )

    async def _run_tickets_polling(self):
        self.__reset_customer_cache()

        total_start_time = time.time()
        logger.info(f"Starting triage process...")

        customer_cache_response = await self._customer_cache_repository.get_cache_for_triage_monitoring()
        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            logger.error(
                f"Error while getting VeloCloud's customer cache: {customer_cache_response}. "
                f"Skipping Triage process..."
            )
            return

        self._customer_cache = customer_cache_response["body"]

        logger.info("Getting all open tickets for all customers...")
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies()
        logger.info(
            f"Got all {len(open_tickets)} open tickets for all customers. "
            f"Filtering them to get only the ones under the device list"
        )
        relevant_open_tickets = self._filter_tickets_and_details_related_to_edges_under_monitoring(open_tickets)
        logger.info(
            f"Got {len(relevant_open_tickets)} relevant tickets for all customers. "
            f"Cleaning them up to exclude all invalid notes..."
        )
        relevant_open_tickets = self._filter_irrelevant_notes_in_tickets(relevant_open_tickets)

        logger.info(f"Splitting relevant tickets in tickets with and without triage...")
        details_with_triage, details_without_triage = self._get_ticket_details_with_and_without_triage(
            relevant_open_tickets
        )

        logger.info(
            f"Ticket details split successfully. "
            f"Ticket details with triage: {len(details_with_triage)}. "
            f"Ticket details without triage: {len(details_without_triage)}. "
            "Processing both sets..."
        )
        self._cached_info_by_serial: dict = {elem["serial_number"]: elem for elem in self._customer_cache}

        await self._build_edges_status_by_serial()
        await asyncio.gather(
            self._process_ticket_details_with_triage(details_with_triage),
            self._process_ticket_details_without_triage(details_without_triage),
        )
        logger.info(f"Triage process finished! took {time.time() - total_start_time} seconds")

    async def _build_edges_status_by_serial(self):
        edge_list = await self._velocloud_repository.get_edges_for_triage()
        edges_network_enterprises = await self._velocloud_repository.get_network_enterprises_for_triage()
        edges_with_ha_info = self._ha_repository.map_edges_with_ha_info(edge_list, edges_network_enterprises)
        all_edges = self._ha_repository.get_edges_with_standbys_as_standalone_edges(edges_with_ha_info)

        for edge in all_edges:
            serial_number = edge["edgeSerialNumber"]
            if serial_number in self._cached_info_by_serial.keys():
                self._edges_status_by_serial[serial_number] = edge
                continue

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets_details = []

        bruin_clients_ids: Set[int] = set(elem["bruin_client_info"]["client_id"] for elem in self._customer_cache)

        logger.info("Getting all open Service Outage tickets...")

        open_tickets_response = await self._bruin_repository.get_open_outage_tickets()
        open_tickets_response_body = open_tickets_response["body"]
        open_tickets_response_status = open_tickets_response["status"]

        if open_tickets_response_status not in range(200, 300):
            logger.error(f"Error while getting open Service Outage tickets: {open_tickets_response}")
            return []

        logger.info(f"Got {len(open_tickets_response_body)} open Service Outage tickets")

        logger.info(
            f"Filtering open Service Outage tickets to keep only those related to customers under monitoring..."
        )
        filtered_ticket_list = [
            ticket for ticket in open_tickets_response_body if ticket["clientID"] in bruin_clients_ids
        ]
        logger.info(
            f"Got {len(filtered_ticket_list)} open Service Outage tickets related to customers under monitoring"
        )

        logger.info("Getting ticket tasks for each open ticket...")
        open_tickets_ids = (ticket["ticketID"] for ticket in filtered_ticket_list)

        tasks = [
            self._get_open_tickets_with_details_by_ticket_id(ticket_id, open_tickets_details)
            for ticket_id in open_tickets_ids
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Finished getting tickets tasks!")

        return open_tickets_details

    async def _get_open_tickets_with_details_by_ticket_id(self, ticket_id, open_tickets_details):
        @retry(
            wait=wait_exponential(
                multiplier=self._config.TRIAGE_CONFIG["multiplier"], min=self._config.TRIAGE_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.TRIAGE_CONFIG["stop_delay"]),
        )
        async def get_open_tickets_with_details_by_ticket_id():
            async with self._semaphore:
                logger.info(f"Getting tasks for ticket {ticket_id}...")

                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                ticket_details_response_body = ticket_details_response["body"]
                ticket_details_response_status = ticket_details_response["status"]

                if ticket_details_response_status not in range(200, 300):
                    logger.error(
                        f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                        f"Skipping getting tasks..."
                    )
                    return

                ticket_details_list = ticket_details_response_body["ticketDetails"]
                if not ticket_details_list:
                    logger.warning(
                        f"Ticket {ticket_id} doesn't have any task under ticketDetails key. "
                        f"Skipping getting tasks..."
                    )
                    return

                logger.info(f"Got tasks for ticket {ticket_id}!")

                open_tickets_details.append(
                    {
                        "ticket_id": ticket_id,
                        "ticket_details": ticket_details_list,
                        "ticket_notes": ticket_details_response_body["ticketNotes"],
                    }
                )

        try:
            await get_open_tickets_with_details_by_ticket_id()
        except Exception as e:
            logger.error(f"An error occurred while trying to get ticket tasks for ticket {ticket_id} -> {e}")

    def _filter_tickets_and_details_related_to_edges_under_monitoring(self, tickets):
        serials_under_monitoring: Set[str] = set(elem["serial_number"] for elem in self._customer_cache)

        logger.info(
            f"Filtering {len(tickets)} tickets and their tasks to keep only those related to edges under "
            f"monitoring..."
        )

        relevant_tickets = []
        for ticket in tickets:
            logger.info(f"Looking for relevant tasks in ticket {ticket['ticket_id']}...")

            ticket_details = ticket["ticket_details"]
            relevant_details = [
                detail for detail in ticket_details if detail["detailValue"] in serials_under_monitoring
            ]

            if not relevant_details:
                logger.info(f'Ticket {ticket["ticket_id"]} has no relevant tasks. Skipping ticket...')
                # Having no relevant tasks means the ticket is not relevant either
                continue

            logger.info(f"Found {len(relevant_details)} relevant tasks for ticket {ticket['ticket_id']}")

            relevant_tickets.append(
                {
                    "ticket_id": ticket["ticket_id"],
                    "ticket_details": relevant_details,
                    "ticket_notes": ticket["ticket_notes"],
                }
            )

        logger.info(f"Found {len(relevant_tickets)} tickets related to edges under monitoring")

        return relevant_tickets

    def _filter_irrelevant_notes_in_tickets(self, tickets):
        serials_under_monitoring: Set[str] = set(elem["serial_number"] for elem in self._customer_cache)

        logger.info(f"Filtering out irrelevant notes from {len(tickets)} tickets...")

        sanitized_tickets = []

        for ticket in tickets:
            logger.info(f"Filtering out irrelevant notes from ticket {ticket['ticket_id']}...")

            relevant_notes = [
                note
                for note in ticket["ticket_notes"]
                if note["serviceNumber"] is not None
                if note["noteValue"] is not None
                if bool(TRIAGE_NOTE_REGEX.match(note["noteValue"]))
            ]

            for index, note in enumerate(relevant_notes):
                service_numbers_in_note = set(note["serviceNumber"])
                relevant_service_numbers = serials_under_monitoring & service_numbers_in_note

                if not relevant_service_numbers:
                    del relevant_notes[index]
                else:
                    relevant_notes[index]["serviceNumber"] = list(relevant_service_numbers)

            logger.info(f"Got {len(relevant_notes)} relevant notes from ticket {ticket['ticket_id']}")

            sanitized_tickets.append(
                {
                    "ticket_id": ticket["ticket_id"],
                    "ticket_details": ticket["ticket_details"],
                    "ticket_notes": relevant_notes,
                }
            )

        logger.info(f"Irrelevant notes filtered out from {len(tickets)} tickets")

        return sanitized_tickets

    def _get_ticket_details_with_and_without_triage(self, tickets) -> tuple:
        ticket_details_with_triage = []
        ticket_details_without_triage = []

        logger.info(f"Generating sets of ticket tasks with and without Triage notes based on {len(tickets)} tickets...")

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            ticket_details = ticket["ticket_details"]
            ticket_notes = ticket["ticket_notes"]

            logger.info(f"Checking {len(ticket_details)} tasks from ticket {ticket_id}...")
            for detail in ticket_details:
                serial_number = detail["detailValue"]
                logger.info(f"Looking for Triage notes in ticket {ticket_id} for edge {serial_number}...")

                notes_related_to_serial = [
                    note
                    for note in ticket_notes
                    if note["serviceNumber"] is not None
                    if serial_number in note["serviceNumber"]
                ]
                detail_object = {
                    "ticket_id": ticket_id,
                    "ticket_detail": detail,
                }
                if not notes_related_to_serial:
                    logger.info(f"No Triage notes found in ticket {ticket_id} for edge {serial_number}")
                    ticket_details_without_triage.append(detail_object)
                else:
                    logger.info(f"Triage notes found in ticket {ticket_id} for edge {serial_number}")
                    detail_object["ticket_notes"] = notes_related_to_serial
                    ticket_details_with_triage.append(detail_object)

                logger.info(f"Finished looking for Triage notes in ticket {ticket_id} for edge {serial_number}")

            logger.info(f"Finished checking {len(ticket_details)} tasks from ticket {ticket_id}")

        logger.info(
            f"Generated {len(ticket_details_with_triage)} tasks with Triage notes and "
            f"{len(ticket_details_without_triage)} tasks without Triage notes"
        )

        return ticket_details_with_triage, ticket_details_without_triage

    async def _process_ticket_details_with_triage(self, ticket_details):
        logger.info(f"Processing {len(ticket_details)} ticket tasks with Triage / Events notes...")

        for detail in ticket_details:
            ticket_id = detail["ticket_id"]
            serial_number = detail["ticket_detail"]["detailValue"]

            logger.info(f"Processing task with Triage / Events note of ticket {ticket_id} for edge {serial_number}...")

            logger.info(
                f"Checking if Events note needs to be appended to task of ticket {ticket_id} "
                f"for edge {serial_number}..."
            )
            newest_triage_note = self._get_most_recent_ticket_note(detail)

            if self._was_ticket_note_appended_recently(newest_triage_note):
                logger.info(
                    f"The last Triage / Events note was appended to task of ticket {ticket_id} for edge "
                    f"{serial_number} not long ago so no new Events note will be appended for now"
                )
                continue

            logger.info(f"Appending Events note to task of ticket {ticket_id} for edge {serial_number}...")

            newest_triage_note_timestamp = newest_triage_note["createdDate"]
            edge_data = self._cached_info_by_serial[serial_number]

            await self._append_new_triage_notes_based_on_recent_events(
                detail, newest_triage_note_timestamp, edge_data["edge"]
            )
            logger.info(f"Events note appended to task of ticket {ticket_id} for edge {serial_number}!")

            logger.info(f"Finished processing task of ticket {ticket_id} for edge {serial_number}!")

        logger.info(f"Finished processing {len(ticket_details)} ticket tasks with Triage / Events notes!")

    @staticmethod
    def _get_most_recent_ticket_note(ticket_detail):
        sorted_notes = sorted(ticket_detail["ticket_notes"], key=lambda note: note["createdDate"])
        return sorted_notes[-1]

    def _was_ticket_note_appended_recently(self, ticket_note):
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note["createdDate"]).astimezone(utc)
        last_note_minutes = self._config.TRIAGE_CONFIG["last_note_minutes"]

        return (current_datetime - ticket_note_creation_datetime) <= timedelta(minutes=last_note_minutes)

    async def _append_new_triage_notes_based_on_recent_events(
        self, ticket_detail, events_lookup_timestamp: str, edge_full_id
    ):
        ticket_id = ticket_detail["ticket_id"]
        service_number = ticket_detail["ticket_detail"]["detailValue"]

        logger.info(f"Appending new triage note to task of ticket {ticket_id} for edge {service_number}...")

        working_environment = self._config.CURRENT_ENVIRONMENT

        past_moment = parse(events_lookup_timestamp).astimezone(utc)
        logger.info(f"Getting events for edge {service_number} in ticket {ticket_id}...")

        recent_events_response = await self._velocloud_repository.get_last_edge_events(edge_full_id, since=past_moment)
        recent_events_response_body = recent_events_response["body"]
        recent_events_response_status = recent_events_response["status"]

        if recent_events_response_status not in range(200, 300):
            logger.error(
                f"Error while getting the last events for edge {service_number}: {recent_events_response}. "
                f"Skipping append Events note to ticket {ticket_id}..."
            )
            return

        if not recent_events_response_body:
            logger.info(
                f"No events were found for edge {service_number} starting from {events_lookup_timestamp}. "
                f"Skipping append Events note to ticket {ticket_id}..."
            )
            return

        recent_events_response_body.sort(key=lambda event: event["eventTime"], reverse=True)

        notes_were_appended = False
        for chunk in self._get_events_chunked(recent_events_response_body):
            logger.info(f"Building Events note with {len(chunk)} events from edge {service_number}...")
            triage_note_contents = self._triage_repository.build_events_note(chunk)

            if working_environment == "production":
                logger.info(
                    f"Appending Events note with {len(chunk)} events from edge {service_number} to "
                    f"ticket {ticket_id}..."
                )
                response = await self._bruin_repository.append_note_to_ticket(
                    ticket_id, triage_note_contents, service_numbers=[service_number]
                )

                if response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while appending Events note with {len(chunk)} events from edge {service_number} to "
                        f"ticket {ticket_id}: {response}"
                    )
                    continue

                logger.info(
                    f"Events note with {len(chunk)} events from edge {service_number} appended to ticket {ticket_id}!"
                )
            else:
                logger.info(
                    f"Not going to append a new Events note to task of ticket {ticket_id} for edge {service_number} "
                    f"as current environment is {working_environment.upper()}. "
                    f"Events note: {triage_note_contents}"
                )

            notes_were_appended = True

        if notes_were_appended:
            await self._notify_triage_note_was_appended_to_ticket(ticket_detail)

    def _get_events_chunked(self, events):
        events_per_chunk: int = self._config.TRIAGE_CONFIG["event_limit"]
        number_of_events = len(events)
        chunks = (events[index : index + events_per_chunk] for index in range(0, number_of_events, events_per_chunk))

        for chunk in chunks:
            yield chunk

    async def _notify_triage_note_was_appended_to_ticket(self, ticket_detail: dict):
        ticket_id = ticket_detail["ticket_id"]
        ticket_detail_id = ticket_detail["ticket_detail"]["detailID"]
        service_number = ticket_detail["ticket_detail"]["detailValue"]

        message = (
            f"Triage appended to detail {ticket_detail_id} (serial: {service_number}) of ticket {ticket_id}. "
            f"Details at https://app.bruin.com/t/{ticket_id}"
        )

        logger.info(message)
        await self._notifications_repository.send_slack_message(message)

    async def _process_ticket_details_without_triage(self, ticket_details):
        logger.info(f"Processing {len(ticket_details)} ticket tasks without Triage note...")

        for detail in ticket_details:
            ticket_id = detail["ticket_id"]
            serial_number = detail["ticket_detail"]["detailValue"]

            logger.info(f"Processing task of ticket {ticket_id} for edge {serial_number} without Triage note...")

            edge_data = self._cached_info_by_serial[serial_number]
            edge_full_id = edge_data["edge"]

            edge_status = self._edges_status_by_serial.get(serial_number)
            if edge_status is None:
                logger.warning(
                    f"No status was found for edge {serial_number} in the mapping between edges' serial numbers and "
                    f"statuses. Skipping append Triage note to task of ticket {ticket_id}..."
                )
                continue

            outage_type = self._outage_repository.get_outage_type_by_edge_status(edge_status)
            if not outage_type:
                logger.info(
                    f"Edge {serial_number} is no longer down, so the initial Triage note won't be posted to ticket "
                    f"{ticket_id}. Posting an Events note of the last 24 hours to the ticket so it's not blank..."
                )

                timestamp_for_events_lookup = str(datetime.now(utc) - timedelta(days=1))
                await self._append_new_triage_notes_based_on_recent_events(
                    detail, timestamp_for_events_lookup, edge_full_id
                )
            else:
                logger.info(
                    f"Edge {serial_number} is in {outage_type.value} state. Posting initial Triage note to ticket "
                    f"{ticket_id}..."
                )

                if not self._outage_repository.should_document_outage(edge_status):
                    logger.info(
                        f"Edge {serial_number} is down, but it doesn't qualify to be documented as a Service Outage in "
                        f"ticket {ticket_id}. Most probable thing is that the edge is the standby of a HA pair, and "
                        "standbys in outage state are only documented in the event of a Soft Down. Skipping..."
                    )
                    continue

                logger.info(f"Getting events for edge {serial_number} in ticket {ticket_id}...")
                past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)
                recent_events_response = await self._velocloud_repository.get_last_edge_events(
                    edge_full_id, since=past_moment_for_events_lookup
                )

                if recent_events_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while getting the last events of edge {serial_number}: {recent_events_response}. "
                        f"Skipping append Triage note to task of ticket {ticket_id}..."
                    )
                    continue

                recent_events = recent_events_response["body"]
                recent_events.sort(key=lambda event: event["eventTime"], reverse=True)

                logger.info(f"Building Triage note with {len(recent_events)} events from edge {serial_number}...")
                ticket_note = self._triage_repository.build_triage_note(
                    edge_data, edge_status, recent_events, outage_type
                )

                logger.info(
                    f"Appending Triage note with {len(recent_events)} events from edge {serial_number} to "
                    f"ticket {ticket_id}..."
                )
                await self._bruin_repository.append_triage_note(detail, ticket_note)

            logger.info(f"Finished processing task of ticket {ticket_id} for edge {serial_number}!")

        logger.info(f"Finished processing {len(ticket_details)} ticket tasks without Triage note!")
