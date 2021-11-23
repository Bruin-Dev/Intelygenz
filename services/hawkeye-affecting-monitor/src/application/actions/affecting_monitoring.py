import asyncio
import os
import re
import time

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc


TEST_TYPE_REGEX_TEMPLATE = (
    r"^#\*(Automation Engine|MetTel's IPA)\*#\nService Affecting \(Ixia\).*Test Type: {test_type}"
)
TEST_STATUS_REGEX_TEMPLATE = (
    r"^#\*(Automation Engine|MetTel's IPA)\*#\nService Affecting \(Ixia\).*Test Status: {test_status}"
)

PASSED_NOTE_REGEX = re.compile(TEST_STATUS_REGEX_TEMPLATE.format(test_status='PASSED'), re.DOTALL)
FAILED_NOTE_REGEX = re.compile(TEST_STATUS_REGEX_TEMPLATE.format(test_status='FAILED'), re.DOTALL)


class AffectingMonitor:
    def __init__(self, logger, scheduler, config, bruin_repository, hawkeye_repository,
                 notifications_repository, customer_cache_repository, utils_repository):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._bruin_repository = bruin_repository
        self._hawkeye_repository = hawkeye_repository
        self._notifications_repository = notifications_repository
        self._customer_cache_repository = customer_cache_repository
        self._utils_repository = utils_repository

        self._bruin_semaphore = asyncio.BoundedSemaphore(config.MONITOR_CONFIG['semaphores']['bruin'])

        self.__reset_state()

    def __reset_state(self):
        self._tickets_by_serial = {}

    async def start_hawkeye_affecting_monitoring(self, exec_on_start):
        self._logger.info('Scheduling Hawkeye Affecting Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Hawkeye Affecting Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._affecting_monitoring_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['affecting_monitor'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_hawkeye_affecting_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Hawkeye Affecting Monitoring job. Reason: {conflict}')

    async def _affecting_monitoring_process(self):
        self.__reset_state()

        self._logger.info(f"Starting Hawkeye Affecting Monitor!")
        start = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        customer_cache: list = customer_cache_response['body']

        probe_uids = self._get_all_probe_uids_from_cache(customer_cache)
        test_results_response = await self._hawkeye_repository.get_tests_results_for_affecting_monitoring(
            probe_uids=probe_uids
        )
        if test_results_response['status'] not in range(200, 300):
            return

        tests_results_by_device: dict = test_results_response['body']
        sorted_tests_results = self._get_tests_results_sorted_by_date_asc(tests_results_by_device)
        cached_devices_mapped_to_tests_results: list = self._map_cached_devices_with_tests_results(
            customer_cache, sorted_tests_results
        )

        self._logger.info(
            f'Looking for Service Affecting tickets for {len(cached_devices_mapped_to_tests_results)} devices...'
        )
        tickets_tasks = [
            self._add_device_to_tickets_mapping(
                serial_number=device['cached_info']['serial_number'],
                bruin_client_id=device['cached_info']['bruin_client_info']['client_id'],
            )
            for device in cached_devices_mapped_to_tests_results
        ]
        await asyncio.gather(*tickets_tasks)

        self._logger.info(f'Processing {len(cached_devices_mapped_to_tests_results)} devices...')
        monitoring_tasks = [
            self._process_device(device_info)
            for device_info in cached_devices_mapped_to_tests_results
        ]
        await asyncio.gather(*monitoring_tasks)

        stop = time.time()
        self._logger.info(f'Hawkeye Affecting Monitor process finished! Took {round((stop - start) / 60, 2)} minutes')

    @staticmethod
    def _get_all_probe_uids_from_cache(customer_cache: list) -> list:
        return [device['probe_uid'] for device in customer_cache]

    @staticmethod
    def _get_tests_results_sorted_by_date_asc(tests_results_by_device: dict) -> dict:
        return {
            probe_uid: sorted(test_results, key=lambda elem: elem['summary']['date'])
            for probe_uid, test_results in tests_results_by_device.items()
        }

    @staticmethod
    def _map_cached_devices_with_tests_results(customer_cache: list, tests_results_by_device: dict) -> list:
        result = []

        for elem in customer_cache:
            probe_uid = elem['probe_uid']

            test_results = tests_results_by_device.get(probe_uid)
            if not test_results:
                continue

            result.append({
                'cached_info': elem,
                'tests_results': test_results,
            })

        return result

    async def _add_device_to_tickets_mapping(self, serial_number: str, bruin_client_id: int):
        async with self._bruin_semaphore:
            affecting_tickets_response = await self._bruin_repository.get_open_affecting_tickets(
                client_id=bruin_client_id, service_number=serial_number
            )

            if affecting_tickets_response['status'] not in range(200, 300):
                return

            affecting_tickets: list = affecting_tickets_response['body']
            if not affecting_tickets:
                self._logger.info(
                    f'No affecting tickets were found for device {serial_number} when building the mapping between '
                    f'this serial and tickets.'
                )

                # Adding the ticket to the serials mapping so new tickets can be created in case FAILED states are
                # spotted later on
                self._tickets_by_serial[serial_number] = {}
                return

            affecting_ticket: dict = affecting_tickets[0]
            ticket_id = affecting_ticket['ticketID']

            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
            if ticket_details_response['status'] not in range(200, 300):
                return

            ticket_details: dict = ticket_details_response['body']
            ticket_details_list = ticket_details['ticketDetails']
            ticket_notes = ticket_details['ticketNotes']

            relevant_detail: dict = self._find_ticket_detail_by_serial(ticket_details_list, serial_number)
            relevant_notes: list = self._find_ticket_notes_by_serial(ticket_notes, serial_number)
            sorted_relevant_notes = self._get_notes_sorted_by_date_and_id_asc(relevant_notes)

            self._tickets_by_serial[serial_number] = {
                'ticket_id': affecting_ticket['ticketID'],
                'detail_id': relevant_detail['detailID'],
                'is_detail_resolved': relevant_detail['detailStatus'] == 'R',
                'initial_notes': [
                    {
                        'text': note['noteValue'],
                        'date': parse(note['createdDate']).astimezone(utc),
                    }
                    for note in sorted_relevant_notes
                ],
                'new_notes': [],
            }

    def _find_ticket_detail_by_serial(self, ticket_details: list, serial_number: str) -> dict:
        return self._utils_repository.get_first_element_matching(
            iterable=ticket_details,
            condition=lambda detail: detail['detailValue'] == serial_number,
        )

    @staticmethod
    def _find_ticket_notes_by_serial(ticket_notes: list, serial_number: str) -> list:
        return [
            note
            for note in ticket_notes
            if serial_number in note['serviceNumber']
            if note['noteValue'] is not None
        ]

    @staticmethod
    def _get_notes_sorted_by_date_and_id_asc(ticket_notes: list) -> list:
        return sorted(ticket_notes, key=lambda note: (note['createdDate'], note['noteId']))

    async def _process_device(self, device_info: dict):
        cached_info = device_info['cached_info']

        serial_number = cached_info['serial_number']
        self._logger.info(f'Processing device {serial_number}...')

        tests_results: list = device_info['tests_results']
        for test_result in tests_results:
            if self._test_result_passed(test_result):
                self._process_passed_test_result(test_result=test_result, device_cached_info=cached_info)
            elif self._test_result_failed(test_result):
                await self._process_failed_test_result(test_result=test_result, device_cached_info=cached_info)
            else:
                self._logger.info(
                    f'Test result {test_result["summary"]["id"]} has state {test_result["summary"]["status"].upper()}. '
                    'Skipping...'
                )

        await self._append_new_notes_for_device(serial_number)

        self._logger.info(f'Finished processing device {serial_number}!')

    async def _append_new_notes_for_device(self, serial_number: str):
        if serial_number not in self._tickets_by_serial:
            self._logger.info(
                f'Serial {serial_number} could not be added to the tickets mapping at the beginning of the '
                f'process, so no notes can be posted to any ticket. Skipping...'
            )
            return

        notes_to_append = self._tickets_by_serial[serial_number].get('new_notes')

        if not notes_to_append:
            self._logger.info(f'No notes to append for serial {serial_number} were found. Skipping...')
            return

        ticket_id = self._tickets_by_serial[serial_number]['ticket_id']

        working_environment = self._config.MONITOR_CONFIG['environment']
        if working_environment != 'production':
            self._logger.info(
                f'{len(notes_to_append)} affecting notes to append to ticket {ticket_id} were found, but the current '
                'environment is not PRODUCTION. Skipping...'
            )
            return

        self._logger.info(
            f'Posting {len(notes_to_append)} affecting notes to ticket {ticket_id} (serial: {serial_number})...'
        )

        notes_objects = [
            {
                'text': note['text'],
                'service_number': serial_number,
            }
            for note in notes_to_append
        ]
        await self._bruin_repository.append_multiple_notes_to_ticket(ticket_id=ticket_id, notes=notes_objects)
        await self._notifications_repository.notify_multiple_notes_were_posted_to_ticket(ticket_id, serial_number)

    @staticmethod
    def _test_result_passed(test_result: dict) -> bool:
        return test_result['summary']['status'] == 'Passed'

    @staticmethod
    def _test_result_failed(test_result: dict) -> bool:
        return test_result['summary']['status'] == 'Failed'

    def _process_passed_test_result(self, test_result: dict, device_cached_info: dict):
        serial_number = device_cached_info['serial_number']
        test_result_id = test_result['summary']['id']
        test_type = test_result['summary']['testType']

        self._logger.info(
            f'Processing PASSED test result {test_result_id} (type: {test_type}) that was run for serial '
            f'{serial_number}...'
        )

        if serial_number not in self._tickets_by_serial:
            self._logger.info(
                f'Serial {serial_number} could not be added to the tickets mapping at the beginning of the '
                f'process, so the current PASSED state for test type {test_type} will be ignored. Skipping...'
            )
            return

        affecting_ticket = self._tickets_by_serial[serial_number]
        if not affecting_ticket:
            self._logger.info(
                f'Serial {serial_number} is not under any affecting ticket and all thresholds are normal for '
                f'test type {test_type}. Skipping...'
            )
            return

        ticket_id = affecting_ticket['ticket_id']
        if affecting_ticket['is_detail_resolved']:
            self._logger.info(
                f'Serial {serial_number} is under an affecting ticket (ID {ticket_id}) whose ticket detail is resolved '
                f'and all thresholds are normal for test type {test_type}, so the current PASSED state will not be '
                'reported. Skipping...'
            )
            return

        ticket_notes: list = affecting_ticket['initial_notes'] + affecting_ticket['new_notes']

        last_note = self._get_last_note_by_test_type(ticket_notes, test_type)
        if not last_note:
            self._logger.info(
                f'No note was found for serial {serial_number} and test type {test_type} in ticket {ticket_id}. '
                'Skipping...'
            )
            return

        note_text = last_note['text']
        if self._is_passed_note(note_text):
            self._logger.info(
                f'Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} '
                f'corresponds to a PASSED state. Skipping...'
            )
            return

        self._logger.info(
            f'Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} '
            'corresponds to a FAILED state. A new note reporting the current PASSED state will be built and appended '
            'to the ticket later on.'
        )

        passed_note = self._build_passed_note(test_result, device_cached_info)
        self._tickets_by_serial[serial_number]['new_notes'].append({
            'text': passed_note,
            'date': datetime.utcnow(),
        })

        self._logger.info(f'Finished processing PASSED test result {test_result_id}!')

    async def _process_failed_test_result(self, test_result: dict, device_cached_info: dict):
        serial_number = device_cached_info['serial_number']
        bruin_client_id = device_cached_info['bruin_client_info']['client_id']

        test_result_id = test_result['summary']['id']
        test_type = test_result['summary']['testType']

        self._logger.info(
            f'Processing FAILED test result {test_result_id} (type: {test_type}) that was run for serial '
            f'{serial_number}...'
        )

        if serial_number not in self._tickets_by_serial:
            self._logger.info(
                f'Serial {serial_number} could not be added to the tickets mapping at the beginning of the '
                f'process, so the current FAILED state for test type {test_type} will be ignored. Skipping...'
            )
            return

        affecting_ticket = self._tickets_by_serial[serial_number]
        if not affecting_ticket:
            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment != 'production':
                self._logger.info(
                    f'Serial {serial_number} is not under any affecting ticket and some troubles were spotted for '
                    f'test type {test_type}, but the current environment is not PRODUCTION. Skipping ticket creation...'
                )
                return

            self._logger.info(
                f'Serial {serial_number} is not under any affecting ticket and some troubles were spotted for '
                f'test type {test_type}. Creating affecting ticket..'
            )

            ticket_creation_response = await self._bruin_repository.create_affecting_ticket(
                client_id=bruin_client_id, service_number=serial_number
            )
            if ticket_creation_response['status'] not in range(200, 300):
                return

            ticket_id: int = ticket_creation_response['body']['ticketIds'][0]
            self._logger.info(
                f'Affecting ticket created for serial {serial_number} (ID: {ticket_id}). A new note reporting the '
                f'current FAILED state for test type {test_type} will be built and appended to the ticket later on.'
            )
            await self._notifications_repository.notify_ticket_creation(ticket_id, serial_number)

            failed_note = self._build_failed_note(test_result, device_cached_info)
            self._tickets_by_serial[serial_number] = {
                'ticket_id': ticket_id,
                'detail_id': None,
                'is_detail_resolved': False,  # The ticket was just created, so assuming the detail is unresolved is OK
                'initial_notes': [],
                'new_notes': [
                    {
                        'text': failed_note,
                        'date': datetime.utcnow(),
                    },
                ],
            }
        else:
            ticket_id = self._tickets_by_serial[serial_number]['ticket_id']
            detail_id = self._tickets_by_serial[serial_number]['detail_id']

            self._logger.info(
                f'Serial {serial_number} is under affecting ticket {ticket_id} and some troubles were spotted for '
                f'test type {test_type}.'
            )

            if self._tickets_by_serial[serial_number]['is_detail_resolved']:
                self._logger.info(
                    f'Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} is '
                    f'currently unresolved and a FAILED state was spotted. Unresolving detail...'
                )

                unresolve_detail_response = await self._bruin_repository.unresolve_ticket_detail(ticket_id, detail_id)
                if unresolve_detail_response['status'] not in range(200, 300):
                    self._logger.info(
                        f'Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} '
                        'could not be unresolved. A note reporting the spotted FAILED state will be built and '
                        'appended to the ticket later on.'
                    )
                else:
                    self._logger.info(
                        f'Ticket detail of affecting ticket {ticket_id} that is related to serial {serial_number} '
                        'was unresolved successfully. A note reporting the spotted FAILED state will be built and '
                        'appended to the ticket later on.'
                    )
                    await self._notifications_repository.notify_ticket_detail_was_unresolved(ticket_id, serial_number)
                    self._tickets_by_serial[serial_number]['is_detail_resolved'] = False

                failed_note = self._build_failed_note(test_result, device_cached_info)
                self._tickets_by_serial[serial_number]['new_notes'].append({
                    'text': failed_note,
                    'date': datetime.utcnow(),
                })
                return

            ticket_notes: list = affecting_ticket['initial_notes'] + affecting_ticket['new_notes']
            last_note = self._get_last_note_by_test_type(ticket_notes, test_type)
            if not last_note:
                self._logger.info(
                    f'No note was found for serial {serial_number} and test type {test_type} in ticket {ticket_id}. '
                    'A new note reporting the current FAILED state for this test type will be built and appended '
                    'to the ticket later on.'
                )

                failed_note = self._build_failed_note(test_result, device_cached_info)
                self._tickets_by_serial[serial_number]['new_notes'].append({
                    'text': failed_note,
                    'date': datetime.utcnow(),
                })
            else:
                note_text = last_note['text']
                if self._is_passed_note(note_text):
                    self._logger.info(
                        f'Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} '
                        f'corresponds to a PASSED state. A new note reporting the current FAILED state for this test '
                        'type will be built and appended to the ticket later on.'
                    )

                    failed_note = self._build_failed_note(test_result, device_cached_info)
                    self._tickets_by_serial[serial_number]['new_notes'].append({
                        'text': failed_note,
                        'date': datetime.utcnow(),
                    })
                else:
                    self._logger.info(
                        f'Last note found for serial {serial_number} and test type {test_type} in ticket {ticket_id} '
                        'corresponds to a previous FAILED state. No new notes will be built to report the current '
                        'FAILED state.'
                    )

        self._logger.info(f'Finished processing FAILED test result {test_result_id}!')

    def _get_last_note_by_test_type(self, notes: list, test_type: str) -> dict:
        test_type_regex = re.compile(TEST_TYPE_REGEX_TEMPLATE.format(test_type=test_type), re.DOTALL)

        return self._utils_repository.get_last_element_matching(
            iterable=notes,
            condition=lambda note: bool(test_type_regex.match(note['text'])),
        )

    @staticmethod
    def _is_passed_note(note: str) -> bool:
        return bool(PASSED_NOTE_REGEX.match(note))

    @staticmethod
    def _build_passed_note(test_result: dict, device_cached_info: dict) -> str:
        return os.linesep.join([
            "#*MetTel's IPA*#",
            'Service Affecting (Ixia)',
            '',
            f'Device Name: {test_result["summary"]["probeFrom"]}',
            f'Device Type: {device_cached_info["device_type_name"]}',
            f'Device Group(s): {device_cached_info["probe_group"]}',
            f'Serial: {device_cached_info["serial_number"]}',
            f'Hawkeye ID: {device_cached_info["probe_id"]}',
            '',
            f'Test Type: {test_result["summary"]["testType"]}',
            f'Test: {test_result["summary"]["testId"]} - Test Result: {test_result["summary"]["id"]}',
            '',
            'All thresholds are normal.',
            '',
            'Test Status: PASSED',
        ])

    @staticmethod
    def _build_failed_note(test_result: dict, device_cached_info: dict) -> str:
        failed_metrics = [
            metric
            for metric in test_result['metrics']
            if metric['status'] == 'Failed'
        ]

        metrics_subnotes = []
        for metric in failed_metrics:
            metrics_subnotes.append(os.linesep.join([
                f'Trouble: {metric["metric"]}',
                f'Threshold: {metric["threshold"]}',
                f'Value: {metric["value"]}',
            ]))

        metrics_for_note = f'{os.linesep}{os.linesep}'.join(metrics_subnotes)

        return os.linesep.join([
            "#*MetTel's IPA*#",
            'Service Affecting (Ixia)',
            '',
            f'Device Name: {test_result["summary"]["probeFrom"]}',
            f'Device Type: {device_cached_info["device_type_name"]}',
            f'Device Group(s): {device_cached_info["probe_group"]}',
            f'Serial: {device_cached_info["serial_number"]}',
            f'Hawkeye ID: {device_cached_info["probe_id"]}',
            '',
            f'Test Type: {test_result["summary"]["testType"]}',
            f'Test: {test_result["summary"]["testId"]} - Test Result: {test_result["summary"]["id"]}',
            '',
            metrics_for_note,
            '',
            'Test Status: FAILED',
        ])
