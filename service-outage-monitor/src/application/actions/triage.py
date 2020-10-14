import asyncio
import re
import time

from datetime import datetime
from datetime import timedelta
from typing import NoReturn
from typing import Set

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from tenacity import retry, wait_exponential, stop_after_delay

from igz.packages.eventbus.eventbus import EventBus

from application.repositories import EdgeIdentifier


class Triage:
    __triage_note_regex = re.compile(r'#\*Automation Engine\*#\nTriage')

    def __init__(self, event_bus: EventBus, logger, scheduler, config, outage_repository,
                 customer_cache_repository, bruin_repository, velocloud_repository, notifications_repository,
                 triage_repository, metrics_repository):
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

        self.__reset_customer_cache()
        self._semaphore = asyncio.BoundedSemaphore(self._config.TRIAGE_CONFIG['semaphore'])

    def __reset_customer_cache(self):
        self._customer_cache = []

    async def start_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every '
                          f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone']))
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
        relevant_open_tickets = self._filter_tickets_related_to_edges_under_monitoring(open_tickets)
        self._logger.info(f'Got all {len(relevant_open_tickets)} relevant tickets for all customers.')

        self._logger.info(f'Splitting relevant tickets in tickets with and without triage...')
        tickets_with_triage, tickets_without_triage = self._distinguish_tickets_with_and_without_triage(
            relevant_open_tickets)

        self._logger.info(f'Tickets split successfully. '
                          f'Tickets with triage: {len(tickets_with_triage)}. '
                          f'Tickets without triage: {len(tickets_without_triage)}. '
                          'Processing both ticket sets...')
        edges_data_by_serial: dict = {
            elem['serial_number']: {'edge_id': elem['edge']}
            for elem in self._customer_cache
        }
        await asyncio.gather(
            self._process_tickets_with_triage(tickets_with_triage, edges_data_by_serial),
            self._process_tickets_without_triage(tickets_without_triage, edges_data_by_serial),
        )
        self._logger.info(f'Triage process finished! took {time.time() - total_start_time} seconds')

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(elem['bruin_client_info']['client_id'] for elem in self._customer_cache)
        tasks = [
            self._get_open_tickets_with_details_by_client_id(client_id, open_tickets)
            for client_id in bruin_clients_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        return open_tickets

    async def _get_open_tickets_with_details_by_client_id(self, client_id, open_tickets):
        @retry(wait=wait_exponential(multiplier=self._config.TRIAGE_CONFIG['multiplier'],
                                     min=self._config.TRIAGE_CONFIG['min']),
               stop=stop_after_delay(self._config.TRIAGE_CONFIG['stop_delay']))
        async def get_open_tickets_with_details_by_client_id():
            async with self._semaphore:
                result = []

                open_tickets_response = await self._bruin_repository.get_open_outage_tickets(client_id)
                open_tickets_response_body = open_tickets_response['body']
                open_tickets_response_status = open_tickets_response['status']

                if open_tickets_response_status not in range(200, 300):
                    self._metrics_repository.increment_open_tickets_errors()
                    raise Exception

                open_tickets_ids = (ticket['ticketID'] for ticket in open_tickets_response_body)

                self._logger.info(f'Getting all opened tickets for Bruin customer {client_id}...')
                for ticket_id in open_tickets_ids:
                    ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                    ticket_details_response_body = ticket_details_response['body']
                    ticket_details_response_status = ticket_details_response['status']

                    if ticket_details_response_status not in range(200, 300):
                        continue

                    ticket_details_list = ticket_details_response_body['ticketDetails']
                    if not ticket_details_list:
                        self._logger.info(f"Ticket {ticket_id} doesn't have any detail under ticketDetails key. "
                                          f"Skipping...")
                        continue

                    self._logger.info(f'Got details for ticket {ticket_id} of Bruin customer {client_id}!')

                    result.append({
                        'ticket_id': ticket_id,
                        'ticket_detail': ticket_details_list[0],
                        'ticket_notes': ticket_details_response_body['ticketNotes'],
                    })

                self._logger.info(f'Finished getting all opened tickets for Bruin customer {client_id}!')
                for ticket_item in result:
                    open_tickets.append(ticket_item)

        try:
            await get_open_tickets_with_details_by_client_id()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to get open tickets with details for Bruin client {client_id} -> {e}"
            )

    def _filter_tickets_related_to_edges_under_monitoring(self, tickets):
        serials_under_monitoring: Set[str] = set(elem['serial_number'] for elem in self._customer_cache)

        return [
            ticket
            for ticket in tickets
            if ticket['ticket_detail']['detailValue'] in serials_under_monitoring
        ]

    def _distinguish_tickets_with_and_without_triage(self, tickets) -> tuple:
        tickets_with_triage = []
        for ticket in tickets:
            self._logger.info(f'Checking if ticket {ticket["ticket_id"]} has a triage note already...')
            for note in ticket['ticket_notes']:
                try:
                    if type(note['noteValue']) != str:
                        self._logger.info(f'Type of note value is {type(note["noteValue"])} and the content is'
                                          f' {note["noteValue"]}')
                        continue
                    if self.__triage_note_regex.match(note['noteValue']):
                        self._logger.info(f'Ticket {ticket["ticket_id"]} has a triage already!')
                        tickets_with_triage.append(ticket)
                        break
                except Exception as ex:
                    self._logger.error("An error occurred while distinguishing tickets with and without triage. Note"
                                       f"causing trouble was {note}")
                    self._logger.error(ex)
        tickets_without_triage = [
            ticket
            for ticket in tickets
            if ticket not in tickets_with_triage
        ]

        return tickets_with_triage, tickets_without_triage

    async def _process_tickets_with_triage(self, tickets, edges_data_by_serial):
        self._logger.info('Processing tickets with triage...')

        self._discard_non_triage_notes(tickets)

        for ticket in tickets:
            self._logger.info(f'Checking if events need to be appended to ticket with triage {ticket["ticket_id"]}...')
            newest_triage_note = self._get_most_recent_ticket_note(ticket)

            if self._was_ticket_note_appended_recently(newest_triage_note):
                self._logger.info(f'The last triage note was appended to ticket {ticket["ticket_id"]} not long ago so '
                                  'no new triage note will be appended for now')
                continue
            self._logger.info(f'Appending events to ticket {ticket["ticket_id"]}...')

            ticket_id = ticket['ticket_id']
            serial_number = ticket['ticket_detail']['detailValue']
            newest_triage_note_timestamp = newest_triage_note['createdDate']
            edge_data = edges_data_by_serial[serial_number]

            await self._append_new_triage_notes_based_on_recent_events(
                ticket_id, newest_triage_note_timestamp, edge_data
            )
            self._logger.info(f'Events appended to ticket {ticket["ticket_id"]}!')
            self._metrics_repository.increment_tickets_with_triage_processed()

        self._logger.info('Finished processing tickets with triage!')

    def _discard_non_triage_notes(self, tickets) -> NoReturn:
        for ticket in tickets:
            ticket_notes = ticket['ticket_notes']

            for index, note in enumerate(ticket['ticket_notes']):
                try:
                    if type(note['noteValue']) != str:
                        self._logger.info(f'Type of note value is {type(note["noteValue"])} '
                                          f'and the content is {note["noteValue"]}')
                        continue
                    is_triage_note = bool(self.__triage_note_regex.match(note['noteValue']))
                    if not is_triage_note:
                        del ticket_notes[index]
                except Exception as ex:
                    self._logger.error("An error occurred while discarding notes not matching triage format. Note "
                                       f"causing troubles was {note}")
                    self._logger.error(ex)

    def _get_most_recent_ticket_note(self, ticket):
        sorted_notes = sorted(ticket['ticket_notes'], key=lambda note: note['createdDate'])
        return sorted_notes[-1]

    def _was_ticket_note_appended_recently(self, ticket_note):
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note['createdDate']).astimezone(utc)

        return (current_datetime - ticket_note_creation_datetime) <= timedelta(minutes=30)

    async def _append_new_triage_notes_based_on_recent_events(self, ticket_id, last_triage_timestamp: str, edge_data):
        self._logger.info(f'Appending new triage note to ticket {ticket_id}...')

        working_environment = self._config.TRIAGE_CONFIG['environment']

        edge_full_id = edge_data['edge_id']
        edge_identifier = EdgeIdentifier(**edge_full_id)

        last_triage_datetime = parse(last_triage_timestamp).astimezone(utc)
        self._logger.info(f'Getting events for edge related to ticket {ticket_id} before applying triage...')

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=last_triage_datetime
        )
        recent_events_response_body = recent_events_response['body']
        recent_events_response_status = recent_events_response['status']

        if recent_events_response_status not in range(200, 300):
            return

        if not recent_events_response_body:
            self._logger.info(
                f'No events were found for edge {edge_identifier} starting from {last_triage_timestamp}. '
                f'Not appending any new triage notes to ticket {ticket_id}.'
            )
            return

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        notes_were_appended = False
        for chunk in self._get_events_chunked(recent_events_response_body):
            triage_note_contents = self._triage_repository.build_events_note(chunk)

            if working_environment == 'production':
                response = await self._bruin_repository.append_note_to_ticket(ticket_id, triage_note_contents)
                if response['status'] == 503:
                    self._metrics_repository.increment_note_append_errors()

                if response['status'] not in range(200, 300):
                    continue

                self._logger.info(f'Triage appended to ticket {ticket_id}!')
                self._metrics_repository.increment_notes_appended()
            else:
                self._logger.info(f'Not going to append a new triage note to ticket {ticket_id} '
                                  f'as current environment '
                                  f'is {working_environment.upper()}. Triage note: {triage_note_contents}')

            notes_were_appended = True

        if notes_were_appended:
            await self._notify_triage_note_was_appended_to_ticket(ticket_id)

    def _get_events_chunked(self, events):
        events_per_chunk: int = self._config.TRIAGE_CONFIG['event_limit']
        number_of_events = len(events)
        chunks = (
            events[index:index + events_per_chunk]
            for index in range(0, number_of_events, events_per_chunk)
        )

        for chunk in chunks:
            yield chunk

    async def _notify_triage_note_was_appended_to_ticket(self, ticket_id):
        message = f'Triage appended to ticket {ticket_id}. Details at https://app.bruin.com/t/{ticket_id}'

        self._logger.info(message)
        await self._notifications_repository.send_slack_message(message)

    async def _process_tickets_without_triage(self, tickets, edges_data_by_serial):
        self._logger.info('Processing tickets without triage...')

        for ticket in tickets:
            serial_number = ticket['ticket_detail']['detailValue']
            edge_data = edges_data_by_serial[serial_number]

            await self._process_single_ticket_without_triage(ticket, edge_data)

        self._logger.info('Finished processing tickets without triage!')

    async def _process_single_ticket_without_triage(self, ticket, edge_data):
        ticket_id = ticket['ticket_id']
        self._logger.info(f'Processing ticket without triage {ticket_id}...')

        edge_full_id = edge_data['edge_id']
        edge_identifier = EdgeIdentifier(**edge_full_id)

        past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=past_moment_for_events_lookup
        )
        recent_events_response_body = recent_events_response['body']
        recent_events_response_status = recent_events_response['status']

        if recent_events_response_status not in range(200, 300):
            return

        if not recent_events_response_body:
            self._logger.info(
                f'No events were found for edge {edge_identifier} starting from {past_moment_for_events_lookup}. '
                f'Not appending the first triage note to ticket {ticket_id}.'
            )
            return

        edge_status_response = await self._velocloud_repository.get_edge_status(edge_full_id)
        edge_status_response_status = edge_status_response['status']
        if edge_status_response_status not in range(200, 300):
            return

        edge_status = edge_status_response['body']['edge_info']

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        ticket_note = self._triage_repository.build_triage_note(edge_full_id, edge_status, recent_events_response_body)

        note_appended = await self._bruin_repository.append_triage_note(ticket_id, ticket_note, edge_status)

        if note_appended == 200:
            self._metrics_repository.increment_tickets_without_triage_processed()
        if note_appended == 503:
            self._metrics_repository.increment_note_append_errors()

        self._logger.info(f'Finished processing ticket without triage {ticket_id}!')
