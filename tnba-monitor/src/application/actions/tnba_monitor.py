import asyncio
import re
import time

from datetime import datetime, timedelta
from typing import Set, Dict
from enum import auto, Enum

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from tenacity import retry, wait_exponential, stop_after_delay

TNBA_NOTE_APPENDED_SUCCESS_MSG = (
    '{notes_count} TNBA note(s) were appended to ticket {ticket_id}: app.bruin.com/t/{ticket_id}'
)

TRIAGE_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nTriage \(VeloCloud\)")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nRe-opening")


class TNBAMonitor:
    def __init__(self, event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                 customer_cache_repository, bruin_repository, velocloud_repository, prediction_repository,
                 notifications_repository, utils_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._t7_repository = t7_repository
        self._ticket_repository = ticket_repository
        self._customer_cache_repository = customer_cache_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._prediction_repository = prediction_repository
        self._notifications_repository = notifications_repository
        self._utils_repository = utils_repository

        self.__reset_state()
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    def __reset_state(self):
        self._customer_cache_by_serial = {}
        self._edge_status_by_serial = {}
        self._tnba_notes_to_append = []

    async def start_tnba_automated_process(self, exec_on_start=False):
        self._logger.info('Scheduling TNBA automated process job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info('TNBA automated process job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                    seconds=self._config.MONITORING_INTERVAL_SECONDS,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of TNBA automated process job. Reason: {conflict}')

    async def _run_tickets_polling(self):
        start_time = time.time()

        self.__reset_state()

        self._logger.info('Starting TNBA process...')

        customer_cache_response = await self._customer_cache_repository.get_cache_for_tnba_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        edges_statuses = await self._velocloud_repository.get_edges_for_tnba_monitoring()
        if not edges_statuses:
            err_msg = 'No edges statuses were received from VeloCloud. Aborting TNBA monitoring...'
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
            return

        customer_cache = customer_cache_response['body']

        self._logger.info('Keeping serials that exist in both the customer cache and the set of edges statuses...')
        customer_cache, edges_statuses = self._filter_edges_in_customer_cache_and_edges_statuses(
            customer_cache, edges_statuses
        )

        self._logger.info('Loading customer cache and edges statuses by serial into the monitor instance...')
        self._customer_cache_by_serial = {
            cached_info['serial_number']: cached_info
            for cached_info in customer_cache
        }
        self._edge_status_by_serial = {
            edge_status['edgeSerialNumber']: edge_status
            for edge_status in edges_statuses
        }

        self._logger.info('Getting all open tickets for all customers...')
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies()

        self._logger.info(
            f'Got {len(open_tickets)} open tickets for all customers. '
            f'Filtering them (and their details) to get only the ones under the device list')
        relevant_open_tickets = self._filter_tickets_and_details_related_to_edges_under_monitoring(open_tickets)

        self._logger.info(
            f'Got {len(relevant_open_tickets)} relevant tickets for all customers. '
            f'Cleaning them up to exclude all invalid notes...'
        )
        relevant_open_tickets = self._filter_irrelevant_notes_in_tickets(relevant_open_tickets)

        self._logger.info('Getting T7 predictions for all relevant open tickets...')
        predictions_by_ticket_id = await self._get_predictions_by_ticket_id(relevant_open_tickets)

        self._logger.info('Removing erroneous T7 predictions...')
        predictions_by_ticket_id = self._remove_erroneous_predictions(predictions_by_ticket_id)

        self._logger.info('Creating detail objects based on all tickets...')
        ticket_detail_objects = self._transform_tickets_into_detail_objects(relevant_open_tickets)

        self._logger.info('Discarding resolved ticket details...')
        ticket_detail_objects = self._filter_resolved_ticket_details(ticket_detail_objects)

        self._logger.info('Discarding ticket details of outage tickets whose last outage happened too recently...')
        ticket_detail_objects = self._filter_outage_ticket_details_based_on_last_outage(ticket_detail_objects)

        self._logger.info('Mapping all ticket details with their predictions...')
        ticket_detail_objects = self._map_ticket_details_with_predictions(
            ticket_detail_objects, predictions_by_ticket_id
        )

        self._logger.info(
            f'{len(ticket_detail_objects)} ticket details were successfully mapped to predictions. '
            'Processing all details...'
        )
        tasks = [
            self._process_ticket_detail(detail_object)
            for detail_object in ticket_detail_objects
        ]
        await asyncio.gather(*tasks)
        self._logger.info('All ticket details were processed.')

        if not self._tnba_notes_to_append:
            self._logger.info('No TNBA notes for append were built for any detail processed.')
        else:
            self._logger.info(f'{len(self._tnba_notes_to_append)} TNBA notes were built for append.')
            await self._append_tnba_notes()

        end_time = time.time()
        self._logger.info(f'TNBA process finished! Took {round((end_time - start_time) / 60, 2)} minutes.')

    @staticmethod
    def _filter_edges_in_customer_cache_and_edges_statuses(customer_cache: list, edges_statuses: list) -> tuple:
        serials_in_customer_cache = set(edge['serial_number'] for edge in customer_cache)
        serials_in_edges_statuses = set(edge['edgeSerialNumber'] for edge in edges_statuses)
        serials_in_both_sets = serials_in_customer_cache & serials_in_edges_statuses

        filtered_customer_cache = [edge for edge in customer_cache if edge['serial_number'] in serials_in_both_sets]
        filtered_edges_statuses = [edge for edge in edges_statuses if edge['edgeSerialNumber'] in serials_in_both_sets]

        return filtered_customer_cache, filtered_edges_statuses

    async def _get_all_open_tickets_with_details_for_monitored_companies(self):
        open_tickets = []

        bruin_clients_ids: Set[int] = set(
            elem['bruin_client_info']['client_id']
            for elem in list(self._customer_cache_by_serial.values())
        )
        tasks = [
            self._get_open_tickets_with_details_by_client_id(client_id, open_tickets)
            for client_id in bruin_clients_ids
        ]
        await asyncio.gather(*tasks)
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

                self._logger.info(f'Getting all opened tickets for Bruin customer {client_id}...')
                for ticket in all_open_tickets:
                    ticket_id = ticket['ticketID']
                    ticket_creation_date = ticket['createDate']
                    ticket_topic = ticket['topic']
                    ticket_creator = ticket['createdBy']
                    ticket_status = ticket['ticketStatus']

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
                        'ticket_creation_date': ticket_creation_date,
                        'ticket_status': ticket_status,
                        'ticket_topic': ticket_topic,
                        'ticket_creator': ticket_creator,
                        'ticket_details': ticket_details_list,
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

    def _filter_tickets_and_details_related_to_edges_under_monitoring(self, tickets):
        serials_under_monitoring: Set[str] = set(self._customer_cache_by_serial.keys())

        relevant_tickets = []
        for ticket in tickets:
            ticket_details = ticket['ticket_details']

            relevant_details = [
                detail
                for detail in ticket_details
                if detail['detailValue'] in serials_under_monitoring
            ]

            if not relevant_details:
                # Having no relevant details means the ticket is not relevant either
                continue

            relevant_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'ticket_creation_date': ticket['ticket_creation_date'],
                'ticket_status': ticket['ticket_status'],
                'ticket_topic': ticket['ticket_topic'],
                'ticket_creator': ticket['ticket_creator'],
                'ticket_details': relevant_details,
                'ticket_notes': ticket['ticket_notes'],
            })

        return relevant_tickets

    def _filter_irrelevant_notes_in_tickets(self, tickets):
        serials_under_monitoring: Set[str] = set(self._customer_cache_by_serial.keys())

        sanitized_tickets = []

        for ticket in tickets:
            relevant_notes = [
                note
                for note in ticket['ticket_notes']
                if note['noteValue'] is not None
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
                'ticket_creation_date': ticket['ticket_creation_date'],
                'ticket_status': ticket['ticket_status'],
                'ticket_topic': ticket['ticket_topic'],
                'ticket_creator': ticket['ticket_creator'],
                'ticket_details': ticket['ticket_details'],
                'ticket_notes': relevant_notes,
            })

        return sanitized_tickets

    async def _get_predictions_by_ticket_id(self, tickets: list) -> dict:
        result = {}

        for ticket in tickets:
            ticket_id = ticket["ticket_id"]
            self._logger.info(f'Claiming T7 predictions for ticket {ticket_id}...')

            task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            if task_history_response['status'] not in range(200, 300):
                continue

            task_history: list = task_history_response['body']
            any_ticket_row_has_asset = any(row.get('Asset') for row in task_history)
            if not any_ticket_row_has_asset:
                self._logger.info(f"Task history of ticket {ticket_id} doesn't have any asset. Skipping...")
                continue

            assets_to_predict = [td['detailValue'] for td in ticket['ticket_details']]

            t7_prediction_response = await self._t7_repository.get_prediction(
                ticket_id,
                task_history,
                assets_to_predict
            )
            if t7_prediction_response['status'] not in range(200, 300):
                continue

            ticket_predictions: list = t7_prediction_response['body']
            if not ticket_predictions:
                self._logger.info(f"There are no predictions for ticket {ticket_id}. Skipping...")
                continue

            result[ticket_id] = ticket_predictions
            self._logger.info(f'T7 predictions found for ticket {ticket_id}!')

        return result

    def _remove_erroneous_predictions(self, predictions_by_ticket_id: dict) -> dict:
        result = {}

        for ticket_id, prediction_objects in predictions_by_ticket_id.items():
            valid_predictions = []

            for prediction_obj in prediction_objects:
                serial_number = prediction_obj['assetId']

                if 'error' in prediction_obj.keys():
                    self._logger.info(
                        f"Prediction for serial {serial_number} in ticket {ticket_id} was found but it contains an "
                        f"error from T7 API -> {prediction_obj['error']}"
                    )
                    continue

                valid_predictions.append(prediction_obj)

            if not valid_predictions:
                self._logger.info(f"All predictions in ticket {ticket_id} were erroneous. Skipping ticket...")
                continue

            result[ticket_id] = valid_predictions

        return result

    @staticmethod
    def _transform_tickets_into_detail_objects(tickets: list) -> list:
        detail_objects = []

        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            ticket_creation_date = ticket['ticket_creation_date']
            ticket_topic = ticket['ticket_topic']
            ticket_creator = ticket['ticket_creator']
            ticket_details = ticket['ticket_details']
            ticket_notes = ticket['ticket_notes']
            ticket_status = ticket['ticket_status']

            for detail in ticket_details:
                serial_number = detail['detailValue']

                notes_related_to_serial = [
                    note
                    for note in ticket_notes
                    if serial_number in note['serviceNumber']
                ]

                detail_object = {
                    'ticket_id': ticket_id,
                    'ticket_creation_date': ticket_creation_date,
                    'ticket_status': ticket_status,
                    'ticket_topic': ticket_topic,
                    'ticket_creator': ticket_creator,
                    'ticket_detail': detail,
                    'ticket_notes': notes_related_to_serial,
                }
                detail_objects.append(detail_object)

        return detail_objects

    def _filter_resolved_ticket_details(self, ticket_details: list) -> list:
        return [
            detail_object
            for detail_object in ticket_details
            if not self._ticket_repository.is_detail_resolved(detail_object['ticket_detail'])
        ]

    def _filter_outage_ticket_details_based_on_last_outage(self, ticket_details: list) -> list:
        result = []

        for detail_object in ticket_details:
            ticket_id = detail_object['ticket_id']
            serial_number = detail_object['ticket_detail']['detailValue']
            ticket_notes = detail_object['ticket_notes']
            ticket_creation_date = detail_object['ticket_creation_date']

            if self._ticket_repository.is_detail_in_outage_ticket(detail_object):
                if self._was_last_outage_detected_recently(ticket_notes, ticket_creation_date):
                    self._logger.info(
                        f'Last outage detected for serial {serial_number} in Service Outage ticket {ticket_id} is '
                        'too recent. Skipping...'
                    )
                    continue

            result.append(detail_object)

        return result

    def _was_last_outage_detected_recently(self, ticket_notes: list, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now().astimezone(utc)
        max_seconds_since_last_outage = self._config.MONITOR_CONFIG['last_outage_seconds']

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])

        last_reopen_note = self._utils_repository.get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.match(note['noteValue'])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        triage_note = self._utils_repository.get_first_element_matching(
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

    def _map_ticket_details_with_predictions(self, ticket_details: list, predictions_by_ticket_id: dict) -> list:
        result = []

        for detail_object in ticket_details:
            ticket_id = detail_object['ticket_id']
            serial_number = detail_object['ticket_detail']['detailValue']
            predictions_for_ticket: list = predictions_by_ticket_id.get(ticket_id)

            if not predictions_for_ticket:
                self._logger.info(
                    f'Ticket {ticket_id} does not have any prediction associated. Skipping serial '
                    f'{serial_number}...'
                )
                continue

            prediction_object_related_to_serial = self._prediction_repository.find_prediction_object_by_serial(
                predictions=predictions_for_ticket,
                serial_number=serial_number,
            )
            if not prediction_object_related_to_serial:
                self._logger.info(
                    f'No predictions were found for ticket {ticket_id} and serial {serial_number}. Skipping...'
                )
                continue

            predictions: list = prediction_object_related_to_serial['predictions']

            result.append({
                **detail_object,
                'ticket_detail_predictions': predictions,
            })

        return result

    async def _process_ticket_detail(self, detail_object: dict):
        async with self._semaphore:
            ticket_creation_date = detail_object['ticket_creation_date']
            ticket_status = detail_object['ticket_status']
            ticket_id = detail_object['ticket_id']
            ticket_detail_id = detail_object['ticket_detail']['detailID']
            ticket_notes = detail_object['ticket_notes']
            serial_number = detail_object['ticket_detail']['detailValue']
            predictions = detail_object['ticket_detail_predictions']

            self._logger.info(
                f'Processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}...'
            )

            newest_tnba_note = self._ticket_repository.find_newest_tnba_note_by_service_number(
                ticket_notes, serial_number
            )
            if newest_tnba_note and not self._ticket_repository.is_tnba_note_old_enough(newest_tnba_note):
                msg = (
                    f'TNBA note found for ticket {ticket_id} and detail {ticket_detail_id} is too recent. '
                    f'Skipping detail...'
                )
                self._logger.info(msg)
                return

            if self._is_new_ticket(ticket_status) and self._is_ticket_old_enough(ticket_creation_date) and \
                    self._config.ENVIRONMENT == 'production' and newest_tnba_note:
                msg = (
                    f"Automation Engine appended a TNBA note for serial {serial_number} in ticket {ticket_id}, "
                    "which has been in the IPA Investigate work queue for a while. The ticket is going to be forwarded "
                    "to the Holmdel NOC Investigate queue."
                )
                self._logger.info(msg)
                await self._bruin_repository.change_detail_work_queue(serial_number, ticket_id, ticket_detail_id,
                                                                      'Holmdel NOC Investigate')

            mapped_predictions = self._prediction_repository.map_request_and_repair_completed_predictions(predictions)

            next_results_response = await self._bruin_repository.get_next_results_for_ticket_detail(
                ticket_id, ticket_detail_id, serial_number
            )
            next_results_response_body = next_results_response['body']
            next_results_response_status = next_results_response['status']
            if next_results_response_status not in range(200, 300):
                return

            self._logger.info(
                f'Filtering predictions available in next results for ticket {ticket_id}, '
                f'detail {ticket_detail_id} and serial {serial_number}...'
            )
            next_results: list = next_results_response_body['nextResults']

            relevant_predictions = self._prediction_repository.filter_predictions_in_next_results(
                mapped_predictions, next_results
            )

            if not relevant_predictions:
                msg = (
                    f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                    f"detail {ticket_detail_id} and serial {serial_number}!"
                )
                self._logger.info(msg)
                return

            self._logger.info(
                f'Predictions available in next results found for ticket {ticket_id}, detail {ticket_detail_id} '
                f'and serial {serial_number}: {relevant_predictions}'
            )

            best_prediction: dict = self._prediction_repository.get_best_prediction(relevant_predictions)

            if newest_tnba_note:
                if not self._prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
                        newest_tnba_note, best_prediction):
                    msg = (
                        f"Best prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} "
                        f"didn't change since the last TNBA note was appended. Skipping detail..."
                    )
                    self._logger.info(msg)
                    return

            self._logger.info(
                f"Building TNBA note from prediction {best_prediction['name']} for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}..."
            )

            tnba_note = None
            if self._prediction_repository.is_request_or_repair_completed_prediction(best_prediction):
                self._logger.info(
                    f'Best prediction found for serial {serial_number} of ticket {ticket_id} is '
                    f'{best_prediction["name"]}. Running autoresolve...'
                )
                autoresolve_status = await self._autoresolve_ticket_detail(
                    detail_object=detail_object,
                    best_prediction=best_prediction
                )

                if autoresolve_status is self.AutoresolveTicketDetailStatus.SUCCESS:
                    await self._t7_repository.post_live_automation_metrics(
                        ticket_id, serial_number, automated_successfully=True
                    )
                    tnba_note: str = self._ticket_repository.build_tnba_note_for_AI_autoresolve(serial_number)
                elif autoresolve_status is self.AutoresolveTicketDetailStatus.SKIPPED:
                    self._logger.info(
                        f'Autoresolve was triggered because the best prediction found for serial {serial_number} of '
                        f'ticket {ticket_id} was {best_prediction["name"]}, but the process failed. A TNBA note with '
                        'this prediction will be built and appended to the ticket later on.'
                    )
                    tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(
                        best_prediction, serial_number
                    )
                elif autoresolve_status is self.AutoresolveTicketDetailStatus.BAD_PREDICTION:
                    await self._t7_repository.post_live_automation_metrics(
                        ticket_id, serial_number, automated_successfully=False
                    )
                    self._logger.info(
                        f'The prediction for serial {serial_number} of ticket {ticket_id} is considered wrong.'
                    )

            else:
                tnba_note: str = self._ticket_repository.build_tnba_note_from_prediction(best_prediction, serial_number)

            if not tnba_note:
                self._logger.info(f'No TNBA note will be appended for serial {serial_number} of ticket {ticket_id}.')
                return

            if self._config.ENVIRONMENT == 'production':
                self._tnba_notes_to_append.append({
                    'ticket_id': ticket_id,
                    'text': tnba_note,
                    'detail_id': ticket_detail_id,
                    'service_number': serial_number,
                })
            elif self._config.ENVIRONMENT == 'dev':
                tnba_message = (
                    f'TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} '
                    f'(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}'
                )
                self._logger.info(tnba_message)
                await self._notifications_repository.send_slack_message(tnba_message)

            self._logger.info(
                f'Finished processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}!'
            )

    class AutoresolveTicketDetailStatus(Enum):
        SUCCESS = auto()
        SKIPPED = auto()
        BAD_PREDICTION = auto()

    async def _autoresolve_ticket_detail(
            self, detail_object: dict, best_prediction: dict
    ) -> AutoresolveTicketDetailStatus:
        ticket_id = detail_object['ticket_id']
        serial_number = detail_object['ticket_detail']['detailValue']

        self._logger.info(f'Running autoresolve for serial {serial_number} of ticket {ticket_id}...')

        if not self._ticket_repository.is_detail_in_outage_ticket(detail_object):
            self._logger.info(
                f'Ticket {ticket_id}, where serial {serial_number} is, is not an outage ticket. Skipping '
                'autoresolve...'
            )
            return self.AutoresolveTicketDetailStatus.SKIPPED

        if not self._ticket_repository.was_ticket_created_by_automation_engine(detail_object):
            self._logger.info(
                f'Ticket {ticket_id}, where serial {serial_number} is, was not created by Automation Engine. '
                'Skipping autoresolve...'
            )
            return self.AutoresolveTicketDetailStatus.SKIPPED

        if not self._prediction_repository.is_prediction_confident_enough(best_prediction):
            self._logger.info(
                f'The confidence of the best prediction found for ticket {ticket_id}, where serial {serial_number} is, '
                f'did not exceed the minimum threshold. Skipping autoresolve...'
            )
            return self.AutoresolveTicketDetailStatus.SKIPPED

        edge_status = self._edge_status_by_serial[serial_number]
        if self._is_there_an_outage(edge_status):
            self._logger.info(
                f'Serial {serial_number} of ticket {ticket_id} is in outage state. Skipping autoresolve...'
            )
            return self.AutoresolveTicketDetailStatus.BAD_PREDICTION

        if not self._config.ENVIRONMENT == 'production':
            self._logger.info(
                f'Detail related to serial {serial_number} of ticket {ticket_id} was about to be resolved, but the '
                f'current environment is {self._config.ENVIRONMENT.upper()}. Skipping autoresolve...'
            )
            return self.AutoresolveTicketDetailStatus.SKIPPED

        ticket_detail_id = detail_object['ticket_detail']['detailID']
        resolve_detail_response = await self._bruin_repository.resolve_ticket_detail(ticket_id, ticket_detail_id)

        if resolve_detail_response['status'] in range(200, 300):
            return self.AutoresolveTicketDetailStatus.SUCCESS
        else:
            return self.AutoresolveTicketDetailStatus.SKIPPED

    async def _append_tnba_notes(self):
        notes_by_ticket_id = {}

        for note_object in self._tnba_notes_to_append:
            ticket_id = note_object['ticket_id']
            tnba_note = note_object['text']
            ticket_detail_id = note_object['detail_id']
            service_number = note_object['service_number']

            notes_by_ticket_id.setdefault(ticket_id, [])
            notes_by_ticket_id[ticket_id].append({
                'text': tnba_note,
                'detail_id': ticket_detail_id,
                'service_number': service_number,
            })

        for ticket_id, notes in notes_by_ticket_id.items():
            self._logger.info(f'Appending {len(notes)} TNBA notes to ticket {ticket_id}...')

            append_notes_response = await self._bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)
            append_notes_response_status = append_notes_response['status']
            if append_notes_response_status not in range(200, 300):
                continue

            slack_message = TNBA_NOTE_APPENDED_SUCCESS_MSG.format(notes_count=len(notes), ticket_id=ticket_id)
            await self._notifications_repository.send_slack_message(slack_message)

    def _is_there_an_outage(self, edge_status: dict) -> bool:
        is_faulty_edge = self._is_faulty_edge(edge_status["edgeState"])
        is_there_any_faulty_link = any(
            self._is_faulty_link(link_status['linkState'])
            for link_status in edge_status['links']
        )

        return is_faulty_edge or is_there_any_faulty_link

    @staticmethod
    def _is_faulty_edge(edge_state: str) -> bool:
        return edge_state == 'OFFLINE'

    @staticmethod
    def _is_faulty_link(link_state: str) -> bool:
        return link_state == 'DISCONNECTED'

    @staticmethod
    def _is_new_ticket(ticket_status: str) -> bool:
        return ticket_status == "New"

    def _is_ticket_old_enough(self, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now().astimezone(utc)
        max_seconds_since_creation = self._config.MONITOR_CONFIG['last_outage_seconds']

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_creation = (current_datetime - ticket_creation_datetime).total_seconds()

        return seconds_elapsed_since_creation >= max_seconds_since_creation
