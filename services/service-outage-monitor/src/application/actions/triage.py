import asyncio
import re
import time

from datetime import datetime
from datetime import timedelta
from typing import Set

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from tenacity import retry, wait_exponential, stop_after_delay

from igz.packages.eventbus.eventbus import EventBus


class Triage:
    __triage_note_regex = re.compile(r"#\*(Automation Engine|MetTel's IPA)\*#\nTriage \(VeloCloud\)")

    def __init__(self, event_bus: EventBus, logger, scheduler, config, outage_repository,
                 customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                 triage_repository, metrics_repository, ha_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._outage_repository = outage_repository
        self._customer_cache_repository = customer_cache_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._metrics_repository = metrics_repository
        self._ha_repository = ha_repository
        self._edges_status_by_serial = {}
        self._cached_info_by_serial = {}
        self.__reset_customer_cache()
        self._semaphore = asyncio.BoundedSemaphore(self._config.TRIAGE_CONFIG['semaphore'])

    def __reset_customer_cache(self):
        self._customer_cache = []

    async def start_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every '
                          f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                minutes=self._config.TRIAGE_CONFIG["polling_minutes"],
                                next_run_time=next_run_time,
                                replace_existing=True, id='_triage_process')

    async def _run_tickets_polling(self):
        self.__reset_customer_cache()

        total_start_time = time.time()
        self._logger.info(f'Starting triage process...')

        customer_cache_response = await self._customer_cache_repository.get_cache_for_triage_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._customer_cache = customer_cache_response['body']

        self._logger.info('Getting all open tickets for all customers...')
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies()
        self._logger.info(
            f'Got all {len(open_tickets)} open tickets for all customers. '
            f'Filtering them to get only the ones under the device list')
        relevant_open_tickets = self._filter_tickets_and_details_related_to_edges_under_monitoring(open_tickets)
        self._logger.info(
            f'Got {len(relevant_open_tickets)} relevant tickets for all customers. '
            f'Cleaning them up to exclude all invalid notes...'
        )
        relevant_open_tickets = self._filter_irrelevant_notes_in_tickets(relevant_open_tickets)

        self._logger.info(f'Splitting relevant tickets in tickets with and without triage...')
        details_with_triage, details_without_triage = self._get_ticket_details_with_and_without_triage(
            relevant_open_tickets)

        self._logger.info(f'Ticket details split successfully. '
                          f'Ticket details with triage: {len(details_with_triage)}. '
                          f'Ticket details without triage: {len(details_without_triage)}. '
                          'Processing both sets...')
        self._cached_info_by_serial: dict = {
            elem['serial_number']: elem
            for elem in self._customer_cache
        }

        await self._build_edges_status_by_serial()
        await asyncio.gather(
            self._process_ticket_details_with_triage(details_with_triage),
            self._process_ticket_details_without_triage(details_without_triage),
        )
        self._logger.info(f'Triage process finished! took {time.time() - total_start_time} seconds')

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

        bruin_clients_ids: Set[int] = set(elem['bruin_client_info']['client_id'] for elem in self._customer_cache)

        open_tickets_response = await self._bruin_repository.get_open_outage_tickets()
        open_tickets_response_body = open_tickets_response['body']
        open_tickets_response_status = open_tickets_response['status']

        if open_tickets_response_status not in range(200, 300):
            self._metrics_repository.increment_open_tickets_errors()
            return []

        filtered_ticket_list = [ticket for ticket in open_tickets_response_body
                                if ticket["clientID"] in bruin_clients_ids]
        self._logger.info("Getting all opened tickets details for each open ticket ...")
        open_tickets_ids = (ticket['ticketID'] for ticket in filtered_ticket_list)

        tasks = [
            self._get_open_tickets_with_details_by_ticket_id(ticket_id, open_tickets_details)
            for ticket_id in open_tickets_ids
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info('Finished getting all opened ticket details!')

        return open_tickets_details

    async def _get_open_tickets_with_details_by_ticket_id(self, ticket_id, open_tickets_details):
        @retry(wait=wait_exponential(multiplier=self._config.TRIAGE_CONFIG['multiplier'],
                                     min=self._config.TRIAGE_CONFIG['min']),
               stop=stop_after_delay(self._config.TRIAGE_CONFIG['stop_delay']))
        async def get_open_tickets_with_details_by_ticket_id():
            async with self._semaphore:
                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                ticket_details_response_body = ticket_details_response['body']
                ticket_details_response_status = ticket_details_response['status']

                if ticket_details_response_status not in range(200, 300):
                    return

                ticket_details_list = ticket_details_response_body['ticketDetails']
                if not ticket_details_list:
                    self._logger.info(f"Ticket {ticket_id} doesn't have any detail under ticketDetails key. "
                                      f"Skipping...")
                    return

                self._logger.info(f'Got details for ticket {ticket_id}!')

                open_tickets_details.append({
                    'ticket_id': ticket_id,
                    'ticket_details': ticket_details_list,
                    'ticket_notes': ticket_details_response_body['ticketNotes'],
                })
        try:
            await get_open_tickets_with_details_by_ticket_id()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to get tickets details for ticket_id {ticket_id} -> {e}"
            )

    def _filter_tickets_and_details_related_to_edges_under_monitoring(self, tickets):
        serials_under_monitoring: Set[str] = set(elem['serial_number'] for elem in self._customer_cache)

        relevant_tickets = []
        for ticket in tickets:
            self._logger.info(f'Checking ticket_id: {ticket["ticket_id"]} for relevant details')
            ticket_details = ticket['ticket_details']

            relevant_details = [
                detail
                for detail in ticket_details
                if detail['detailValue'] in serials_under_monitoring
            ]

            if not relevant_details:
                self._logger.info(f'Ticket with ticket_id: {ticket["ticket_id"]} has no relevant details')
                # Having no relevant details means the ticket is not relevant either
                continue

            self._logger.info(f'Ticket with ticket_id: {ticket["ticket_id"]} contains relevant details.'
                              f'Appending to relevant_tickets list ...')
            relevant_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_details': relevant_details,
                'ticket_notes': ticket['ticket_notes'],
            })

        return relevant_tickets

    def _filter_irrelevant_notes_in_tickets(self, tickets):
        serials_under_monitoring: Set[str] = set(elem['serial_number'] for elem in self._customer_cache)

        sanitized_tickets = []

        for ticket in tickets:
            self._logger.info(f'Filtering notes for ticket_id: {ticket["ticket_id"]} to contain relevant notes')

            relevant_notes = [
                note
                for note in ticket['ticket_notes']
                if note['noteValue'] is not None
                if bool(self.__triage_note_regex.match(note['noteValue']))
            ]

            for index, note in enumerate(relevant_notes):
                service_numbers_in_note = set(note['serviceNumber'])
                relevant_service_numbers = serials_under_monitoring & service_numbers_in_note

                if not relevant_service_numbers:
                    del relevant_notes[index]
                else:
                    relevant_notes[index]['serviceNumber'] = list(relevant_service_numbers)

            sanitized_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_details': ticket['ticket_details'],
                'ticket_notes': relevant_notes,
            })

        return sanitized_tickets

    def _get_ticket_details_with_and_without_triage(self, tickets) -> tuple:
        ticket_details_with_triage = []
        ticket_details_without_triage = []

        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            ticket_details = ticket['ticket_details']
            ticket_notes = ticket['ticket_notes']
            self._logger.info(f'Checking details of ticket_id: {ticket_id}')

            for detail in ticket_details:
                serial_number = detail['detailValue']
                self._logger.info(f'Checking for triage notes in ticket_id: {ticket_id} '
                                  f'relating to serial number: {serial_number}')

                notes_related_to_serial = [
                    note
                    for note in ticket_notes
                    if serial_number in note['serviceNumber']
                ]
                detail_object = {
                    'ticket_id': ticket_id,
                    'ticket_detail': detail,
                }
                if not notes_related_to_serial:
                    self._logger.info(f'No triage notes found in ticket_id: {ticket_id} '
                                      f'for serial number {serial_number}. '
                                      f'Adding to ticket_details_without_triage list...')
                    ticket_details_without_triage.append(detail_object)
                else:
                    self._logger.info(f'Triage note found in ticket_id: {ticket_id} '
                                      f'for serial number {serial_number}. '
                                      f'Adding to ticket_details_with_triage list...')
                    detail_object['ticket_notes'] = notes_related_to_serial
                    ticket_details_with_triage.append(detail_object)

        return ticket_details_with_triage, ticket_details_without_triage

    async def _process_ticket_details_with_triage(self, ticket_details):
        self._logger.info('Processing ticket details with triage...')

        for detail in ticket_details:
            ticket_id = detail['ticket_id']
            ticket_detail_id = detail['ticket_detail']['detailID']
            serial_number = detail['ticket_detail']['detailValue']

            self._logger.info(f'Processing detail {ticket_detail_id} with triage of ticket {ticket_id}...')

            self._logger.info(
                f'Checking if events need to be appended to detail {ticket_detail_id} of ticket {ticket_id}...'
            )
            newest_triage_note = self._get_most_recent_ticket_note(detail)

            if self._was_ticket_note_appended_recently(newest_triage_note):
                self._logger.info(
                    f'The last triage note was appended to detail {ticket_detail_id} of ticket '
                    f'{ticket_id} not long ago so no new triage note will be appended for now'
                )
                continue

            self._logger.info(f'Appending events to detail {ticket_detail_id} of ticket {ticket_id}...')

            newest_triage_note_timestamp = newest_triage_note['createdDate']
            edge_data = self._cached_info_by_serial[serial_number]

            await self._append_new_triage_notes_based_on_recent_events(detail, newest_triage_note_timestamp,
                                                                       edge_data['edge'])
            self._logger.info(f'Events appended to detail {ticket_detail_id} of ticket {ticket_id}!')
            self._metrics_repository.increment_tickets_with_triage_processed()

            self._logger.info(f'Finished processing detail {ticket_detail_id} of ticket {ticket_id}!')

        self._logger.info('Finished processing ticket details with triage!')

    @staticmethod
    def _get_most_recent_ticket_note(ticket_detail):
        sorted_notes = sorted(ticket_detail['ticket_notes'], key=lambda note: note['createdDate'])
        return sorted_notes[-1]

    @staticmethod
    def _was_ticket_note_appended_recently(ticket_note):
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note['createdDate']).astimezone(utc)

        return (current_datetime - ticket_note_creation_datetime) <= timedelta(minutes=30)

    async def _append_new_triage_notes_based_on_recent_events(self, ticket_detail, events_lookup_timestamp: str,
                                                              edge_full_id):
        ticket_id = ticket_detail['ticket_id']
        ticket_detail_id = ticket_detail['ticket_detail']['detailID']
        service_number = ticket_detail['ticket_detail']['detailValue']

        self._logger.info(f'Appending new triage note to detail {ticket_detail_id} of ticket {ticket_id}...')

        working_environment = self._config.CURRENT_ENVIRONMENT

        past_moment = parse(events_lookup_timestamp).astimezone(utc)
        self._logger.info(
            f'Getting events for serial {service_number} (detail {ticket_detail_id}) in ticket '
            f'{ticket_id} before applying triage...'
        )

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=past_moment
        )
        recent_events_response_body = recent_events_response['body']
        recent_events_response_status = recent_events_response['status']

        if recent_events_response_status not in range(200, 300):
            return

        if not recent_events_response_body:
            self._logger.info(
                f'No events were found for edge {service_number} starting from {events_lookup_timestamp}. '
                f'Not appending any new triage notes to detail {ticket_detail_id} of ticket {ticket_id}.'
            )
            return

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        notes_were_appended = False
        for chunk in self._get_events_chunked(recent_events_response_body):
            triage_note_contents = self._triage_repository.build_events_note(chunk)

            if working_environment == 'production':
                response = await self._bruin_repository.append_note_to_ticket(
                    ticket_id, triage_note_contents, service_numbers=[service_number]
                )
                if response['status'] == 503:
                    self._metrics_repository.increment_note_append_errors()

                if response['status'] not in range(200, 300):
                    continue

                self._logger.info(f'Triage appended to detail {ticket_detail_id} of ticket {ticket_id}!')
                self._metrics_repository.increment_notes_appended()
            else:
                self._logger.info(
                    f'Not going to append a new triage note to detail {ticket_detail_id} of ticket '
                    f'{ticket_id} as current environment is {working_environment.upper()}. '
                    f'Triage note: {triage_note_contents}')

            notes_were_appended = True

        if notes_were_appended:
            await self._notify_triage_note_was_appended_to_ticket(ticket_detail)

    def _get_events_chunked(self, events):
        events_per_chunk: int = self._config.TRIAGE_CONFIG['event_limit']
        number_of_events = len(events)
        chunks = (
            events[index:index + events_per_chunk]
            for index in range(0, number_of_events, events_per_chunk)
        )

        for chunk in chunks:
            yield chunk

    async def _notify_triage_note_was_appended_to_ticket(self, ticket_detail: dict):
        ticket_id = ticket_detail['ticket_id']
        ticket_detail_id = ticket_detail['ticket_detail']['detailID']
        service_number = ticket_detail['ticket_detail']['detailValue']

        message = (
            f'Triage appended to detail {ticket_detail_id} (serial: {service_number}) of ticket {ticket_id}. '
            f'Details at https://app.bruin.com/t/{ticket_id}'
        )

        self._logger.info(message)
        await self._notifications_repository.send_slack_message(message)

    async def _process_ticket_details_without_triage(self, ticket_details):
        self._logger.info('Processing ticket details without triage...')

        for detail in ticket_details:
            ticket_id = detail['ticket_id']
            ticket_detail_id = detail['ticket_detail']['detailID']
            serial_number = detail['ticket_detail']['detailValue']

            self._logger.info(f'Processing detail {ticket_detail_id} without triage of ticket {ticket_id}...')

            edge_data = self._cached_info_by_serial[serial_number]
            edge_full_id = edge_data['edge']

            edge_status = self._edges_status_by_serial.get(serial_number)
            if edge_status is None:
                continue

            outage_type = self._outage_repository.get_outage_type_by_edge_status(edge_status)
            if not outage_type:
                self._logger.info(
                    f"Edge {serial_number} is no longer down, so the initial triage note won't be posted to ticket "
                    f"{ticket_id}. Posting events of the last 24 hours to the ticket so it's not blank..."
                )

                timestamp_for_events_lookup = str(datetime.now(utc) - timedelta(days=1))
                await self._append_new_triage_notes_based_on_recent_events(
                    detail, timestamp_for_events_lookup, edge_full_id
                )
            else:
                self._logger.info(
                    f"Edge {serial_number} is in {outage_type.value} state. Posting initial triage note to ticket "
                    f"{ticket_id}..."
                )

                if not self._outage_repository.should_document_outage(edge_status):
                    self._logger.info(
                        f"Edge {serial_number} is down, but it doesn't qualify to be documented as a Service Outage in "
                        f"ticket {ticket_id}. Most probable thing is that the edge is the standby of a HA pair, and "
                        "standbys in outage state are only documented in the event of a Soft Down. Skipping..."
                    )
                    continue

                past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)
                recent_events_response = await self._velocloud_repository.get_last_edge_events(
                    edge_full_id, since=past_moment_for_events_lookup
                )

                if recent_events_response['status'] not in range(200, 300):
                    continue

                recent_events = recent_events_response['body']
                recent_events.sort(key=lambda event: event['eventTime'], reverse=True)

                ticket_note = self._triage_repository.build_triage_note(
                    edge_data, edge_status, recent_events, outage_type
                )
                note_appended = await self._bruin_repository.append_triage_note(detail, ticket_note)

                if note_appended == 200:
                    self._metrics_repository.increment_tickets_without_triage_processed()
                if note_appended == 503:
                    self._metrics_repository.increment_note_append_errors()

            self._logger.info(f'Finished processing detail {ticket_detail_id} of ticket {ticket_id}!')

        self._logger.info('Finished processing ticket details without triage!')
