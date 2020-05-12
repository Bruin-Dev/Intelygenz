import asyncio

from datetime import datetime
from typing import Set

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from tenacity import retry, wait_exponential, stop_after_delay


class TNBAMonitor:
    def __init__(self, event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                 monitoring_map_repository, bruin_repository, velocloud_repository, prediction_repository,
                 notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._t7_repository = t7_repository
        self._ticket_repository = ticket_repository
        self._monitoring_map_repository = monitoring_map_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._prediction_repository = prediction_repository
        self._notifications_repository = notifications_repository

        self._monitoring_mapping = {}
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    def __refresh_monitoring_mapping(self):
        self._monitoring_mapping = self._monitoring_map_repository.get_monitoring_map_cache()

    async def start_tnba_automated_process(self, exec_on_start=False):
        self._logger.info('Scheduling TNBA automated process job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info('TNBA automated process job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._tnba_automated_process, 'interval',
                                    seconds=self._config.MONITORING_INTERVAL_SECONDS,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_tnba_automated_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of TNBA automated process job. Reason: {conflict}')

    async def _tnba_automated_process(self):
        self._logger.info('Starting TNBA process...')
        if not self._monitoring_mapping:
            self._logger.info('Creating map with all customers and all their devices...')
            await self._monitoring_map_repository.map_bruin_client_ids_to_edges_serials_and_statuses()
            await self._monitoring_map_repository.start_create_monitoring_map_job(exec_on_start=False)
            self._logger.info('Map of devices by customer created')

        self.__refresh_monitoring_mapping()

        tickets = await self._get_relevant_tickets()
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            self._logger.info(f'Processing ticket with ID {ticket_id}...')
            await self._process_ticket(ticket)
            self._logger.info(f'Finished processing ticket with ID {ticket_id}!')

        self._logger.info('TNBA process finished!')

    async def _get_relevant_tickets(self) -> list:
        self._logger.info('Getting all open tickets for all customers...')
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies()
        self._logger.info(
            f'Got {len(open_tickets)} open tickets for all customers. '
            f'Filtering them to get only the ones under the device list')
        relevant_open_tickets = self._filter_tickets_related_to_edges_under_monitoring(open_tickets)
        self._logger.info(f'Got {len(relevant_open_tickets)} relevant tickets for all customers.')

        return relevant_open_tickets

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(self._monitoring_mapping.keys())
        tasks = [
            self._get_open_tickets_with_details_by_client_id(client_id, open_tickets)
            for client_id in bruin_clients_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        return open_tickets

    async def _get_open_tickets_with_details_by_client_id(self, client_id, open_tickets):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def get_open_tickets_with_details_by_client_id():
            async with self._semaphore:
                result = []

                open_outage_tickets_response = await self._bruin_repository.get_open_outage_tickets(client_id)
                open_outage_tickets_response_body = open_outage_tickets_response['body']
                open_outage_tickets_response_status = open_outage_tickets_response['status']
                if open_outage_tickets_response_status not in range(200, 300):
                    open_outage_tickets_response_body = []

                open_affecting_tickets_response = await self._bruin_repository.get_open_affecting_tickets(client_id)
                open_affecting_tickets_response_body = open_affecting_tickets_response['body']
                open_affecting_tickets_response_status = open_affecting_tickets_response['status']
                if open_affecting_tickets_response_status not in range(200, 300):
                    open_affecting_tickets_response_body = []

                all_open_tickets: list = open_outage_tickets_response_body + open_affecting_tickets_response_body
                open_tickets_ids = (ticket['ticketID'] for ticket in all_open_tickets)

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
        serials_under_monitoring: Set[str] = set(sum(
            (
                list(edge_status_by_serial_dict.keys())
                for edge_status_by_serial_dict in self._monitoring_mapping.values()
            ),
            []
        ))

        return [
            ticket
            for ticket in tickets
            if ticket['ticket_detail']['detailValue'] in serials_under_monitoring
        ]

    async def _process_ticket(self, ticket: dict):
        ticket_id = ticket["ticket_id"]
        serial_number = ticket['ticket_detail']['detailValue']

        self._logger.info(f'Looking for the last TNBA note appended to ticket {ticket_id}...')
        ticket_notes = ticket['ticket_notes']
        newest_tnba_note = self._ticket_repository.find_newest_tnba_note(ticket_notes)
        if not newest_tnba_note:
            self._logger.info(f"Looks like ticket {ticket_id} doesn't have any TNBA note yet")

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                return

            prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
                t7_prediction_response_body, serial_number
            )
            if not prediction_object_for_serial:
                self._logger.info(f"No predictions were found for serial {serial_number} and ticket {ticket_id}!")
                return

            self._logger.info(
                f"Building TNBA note from predictions found for serial {serial_number} and ticket {ticket_id}..."
            )
            predictions: list = prediction_object_for_serial['predictions']
            best_prediction: dict = self._prediction_repository.get_best_prediction(predictions)
        else:
            self._logger.info(f"TNBA note found for ticket {ticket_id}")
            if not self._ticket_repository.is_tnba_note_old_enough(newest_tnba_note):
                self._logger.info(f'TNBA note found for ticket {ticket_id} is too recent. Skipping ticket...')
                return

            t7_prediction_response = await self._t7_repository.get_prediction(ticket_id)
            t7_prediction_response_body = t7_prediction_response['body']
            t7_prediction_response_status = t7_prediction_response['status']
            if t7_prediction_response_status not in range(200, 300):
                return

            prediction_object_for_serial: dict = self._prediction_repository.find_prediction_object_by_serial(
                t7_prediction_response_body, serial_number
            )
            if not prediction_object_for_serial:
                self._logger.info(f"No predictions were found for serial {serial_number} and ticket {ticket_id}!")
                return

            predictions: list = prediction_object_for_serial['predictions']
            best_prediction: dict = self._prediction_repository.get_best_prediction(predictions)
            if not self._prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
                    newest_tnba_note, best_prediction):
                self._logger.info(
                    f"Predictions for serial {serial_number} and ticket {ticket_id} didn't change since the last TNBA"
                    f"note was appended. Skipping ticket..."
                )
                return

        if self._config.ENVIRONMENT == 'production':
            self._logger.info(
                f"Building TNBA note from predictions found for serial {serial_number} and ticket {ticket_id}..."
            )
            tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction)

            self._logger.info(f'Appending TNBA note to ticket {ticket_id}...')
            await self._bruin_repository.append_note_to_ticket(ticket_id, tnba_note, is_private=True)
        elif self._config.ENVIRONMENT == 'dev':
            tnba_message = f'TNBA note would have been appended to ticket {ticket_id} (serial: {serial_number})'
            self._logger.info(tnba_message)
            await self._notifications_repository.send_slack_message(tnba_message)
