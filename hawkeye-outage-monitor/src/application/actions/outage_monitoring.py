import asyncio
import time
import os
import re

from datetime import datetime
from datetime import timedelta
from typing import Callable

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc


TRIAGE_NOTE_REGEX = re.compile(r'^#\*Automation Engine\*#\nTriage \(Ixia\)')
REOPEN_NOTE_REGEX = re.compile(r'^#\*Automation Engine\*#\nRe-opening')


class OutageMonitor:
    def __init__(self, event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                 notifications_repository, customer_cache_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._bruin_repository = bruin_repository
        self._hawkeye_repository = hawkeye_repository
        self._notifications_repository = notifications_repository
        self._customer_cache_repository = customer_cache_repository

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphore'])

    async def start_hawkeye_outage_monitoring(self, exec_on_start):
        self._logger.info('Scheduling Hawkeye Outage Monitor job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG['timezone'])
            next_run_time = datetime.now(tz)
            self._logger.info('Hawkeye Outage Monitor job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._outage_monitoring_process, 'interval',
                                    seconds=self._config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_hawkeye_outage_monitor_process')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of Hawkeye Outage Monitoring job. Reason: {conflict}')

    async def _outage_monitoring_process(self):
        self._logger.info(f"Starting Hawkeye Outage Monitor!")
        start = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_outage_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        customer_cache: list = customer_cache_response['body']

        probes_response = await self._hawkeye_repository.get_probes()
        if probes_response['status'] not in range(200, 300):
            return

        probes: list = probes_response['body']
        if not probes:
            self._logger.info("The list of probes arrived empty. Skipping monitoring process...")
            return

        active_probes = [probe for probe in probes if self._is_active_probe(probe)]
        if not active_probes:
            self._logger.info("All probes were detected as inactive. Skipping monitoring process...")
            return

        probes_with_cache_info = self._map_probes_info_with_customer_cache(active_probes, customer_cache)

        outage_devices = [
            device
            for device in probes_with_cache_info
            if self._is_there_an_outage(device['device_info'])
        ]
        healthy_devices = [device for device in probes_with_cache_info if device not in outage_devices]

        if outage_devices:
            self._logger.info(
                f"{len(outage_devices)} devices were detected in outage state. "
                "Scheduling re-check job for all of them..."
            )
            self._schedule_recheck_job_for_devices(outage_devices)
        else:
            self._logger.info("No devices were detected in outage state. Re-check job won't be scheduled")

        if healthy_devices:
            self._logger.info(
                f"{len(healthy_devices)} devices were detected in healthy state. Running autoresolve for all of them")
            autoresolve_tasks = [self._run_ticket_autoresolve(device) for device in healthy_devices]
            await asyncio.gather(*autoresolve_tasks)
        else:
            self._logger.info("No devices were detected in healthy state. Autoresolve won't be triggered")

        stop = time.time()
        self._logger.info(f'Hawkeye Outage Monitor process finished! Took {round((stop - start) / 60, 2)} minutes')

    async def _run_ticket_autoresolve(self, device: dict):
        async with self._semaphore:
            serial_number = device['cached_info']['serial_number']
            self._logger.info(f'Starting autoresolve for device {serial_number}...')
            client_id = device['cached_info']['bruin_client_info']['client_id']
            outage_ticket_response = await self._bruin_repository.get_open_outage_tickets(
                client_id, service_number=serial_number
            )
            outage_ticket_response_body = outage_ticket_response['body']
            outage_ticket_response_status = outage_ticket_response['status']
            if outage_ticket_response_status not in range(200, 300):
                return

            if not outage_ticket_response_body:
                self._logger.info(f'No open outage ticket found for device {serial_number}. '
                                  f'Skipping autoresolve...')
                return

            outage_ticket: dict = outage_ticket_response_body[0]
            outage_ticket_id = outage_ticket['ticketID']
            outage_ticket_creation_date = outage_ticket['createDate']

            ticket_details_response = await self._bruin_repository.get_ticket_details(outage_ticket_id)
            ticket_details_response_body = ticket_details_response['body']
            ticket_details_response_status = ticket_details_response['status']
            if ticket_details_response_status not in range(200, 300):
                return

            notes_from_outage_ticket = ticket_details_response_body['ticketNotes']
            relevant_notes = [note for note in notes_from_outage_ticket if serial_number in note['serviceNumber']]
            if not self._was_last_outage_detected_recently(relevant_notes, outage_ticket_creation_date):
                self._logger.info(
                    f'Device {device} has been in outage state for a long time, so detail {client_id} '
                    f'(serial {serial_number}) of ticket {outage_ticket_id} will not be autoresolved. Skipping '
                    f'autoresolve...'
                )
                return

            can_ticket_be_autoresolved_one_more_time = self.is_outage_ticket_auto_resolvable(
                relevant_notes, max_autoresolves=3
            )
            if not can_ticket_be_autoresolved_one_more_time:
                self._logger.info(f'Limit to autoresolve ticket {outage_ticket_id} linked to device '
                                  f'{serial_number} has been maxed out already. Skipping autoresolve...')
                return

            details_from_ticket = ticket_details_response_body['ticketDetails']
            detail_for_ticket_resolution = self._get_first_element_matching(
                details_from_ticket,
                lambda detail: detail['detailValue'] == serial_number,
            )
            ticket_detail_id = detail_for_ticket_resolution['detailID']
            if self._is_detail_resolved(detail_for_ticket_resolution):
                self._logger.info(
                    f'Detail {ticket_detail_id} of ticket {outage_ticket_id} is already resolved. '
                    f'Skipping autoresolve...')
                return

            working_environment = self._config.MONITOR_CONFIG['environment']
            if working_environment != 'production':
                self._logger.info(
                    f'Skipping autoresolve for device {serial_number} since the '
                    f'current environment is {working_environment.upper()}.')
                return

            self._logger.info(
                f'Autoresolving detail {ticket_detail_id} (serial: {serial_number}) of ticket {outage_ticket_id}...')
            resolve_ticket_response = await self._bruin_repository.resolve_ticket(
                outage_ticket_id, ticket_detail_id
            )
            if resolve_ticket_response['status'] not in range(200, 300):
                return

            await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)
            await self._notify_successful_autoresolve(outage_ticket_id, ticket_detail_id)

            self._logger.info(
                f'Ticket {outage_ticket_id} linked to device {serial_number} was autoresolved!')

    @staticmethod
    def is_outage_ticket_auto_resolvable(ticket_notes: list, max_autoresolves: int) -> bool:
        regex = re.compile(r"^#\*Automation Engine\*#\nAuto-resolving detail for serial")
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note['noteValue']
            times_autoresolved += bool(regex.match(note_value))

            if times_autoresolved >= max_autoresolves:
                return False

        return True

    def _get_last_element_matching(self, iterable, condition: Callable, fallback=None):
        return self._get_first_element_matching(reversed(iterable), condition, fallback)

    async def _notify_successful_autoresolve(self, ticket_id, detail_id):
        message = f'Detail {detail_id} of outage ticket {ticket_id} ' \
                  f'was autoresolved: https://app.bruin.com/t/{ticket_id}'
        await self._notifications_repository.send_slack_message(message)

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail['detailStatus'] == 'R'

    @staticmethod
    def _is_active_probe(probe: dict) -> bool:
        return int(probe['active']) == 1

    @staticmethod
    def _is_there_an_outage(probe: dict) -> bool:
        return probe['nodetonode']['status'] == 0 or probe['realservice']['status'] == 0

    def _map_probes_info_with_customer_cache(self, probes: list, customer_cache: list) -> list:
        result = []

        probes_by_serial_number = {probe['serialNumber']: probe for probe in probes}
        cached_devices_by_serial_number = {device['serial_number']: device for device in customer_cache}

        for serial_number, probe in probes_by_serial_number.items():
            cached_info = cached_devices_by_serial_number.get(serial_number)
            if not cached_info:
                self._logger.info(f'No cached info was found for device {serial_number}. Skipping...')
                continue

            result.append({
                'device_info': probe,
                'cached_info': cached_info,
            })

        return result

    def _schedule_recheck_job_for_devices(self, devices: list):
        self._logger.info(f'Scheduling recheck job for {len(devices)} devices in outage state...')

        tz = timezone(self._config.MONITOR_CONFIG['timezone'])
        current_datetime = datetime.now(tz)
        run_date = current_datetime + timedelta(seconds=self._config.MONITOR_CONFIG['jobs_intervals']['quarantine'])

        self._scheduler.add_job(self._recheck_devices_for_ticket_creation, 'date',
                                args=[devices],
                                run_date=run_date,
                                replace_existing=False,
                                misfire_grace_time=9999,
                                id=f'_ticket_creation_recheck',
                                )

        self._logger.info(f'Devices scheduled for recheck successfully')

    async def _recheck_devices_for_ticket_creation(self, devices: list):
        self._logger.info(f'Re-checking {len(devices)} devices in outage state prior to ticket creation...')

        probes_response = await self._hawkeye_repository.get_probes()
        if probes_response['status'] not in range(200, 300):
            return

        probes: list = probes_response['body']
        if not probes:
            self._logger.info("The list of probes arrived empty. Skipping monitoring process...")
            return

        active_probes = [probe for probe in probes if self._is_active_probe(probe)]
        if not active_probes:
            self._logger.info("All probes were detected as inactive. Skipping monitoring process...")
            return

        customer_cache_for_outage_devices = [elem['cached_info'] for elem in devices]
        probes_with_cache_info = self._map_probes_info_with_customer_cache(
            active_probes, customer_cache_for_outage_devices
        )

        devices_still_in_outage = [
            device
            for device in probes_with_cache_info
            if self._is_there_an_outage(device['device_info'])
        ]
        healthy_devices = [device for device in probes_with_cache_info if device not in devices_still_in_outage]

        working_environment = self._config.MONITOR_CONFIG['environment']
        if working_environment != 'production':
            self._logger.info(
                f'Process cannot keep going as the current environment is {working_environment.upper()}. '
                f'Healthy devices: {len(healthy_devices)} | Outage devices: {len(devices_still_in_outage)}'
            )
            return

        if devices_still_in_outage:
            self._logger.info(
                f"{len(devices_still_in_outage)} devices were detected as still in outage state after re-check."
            )

            for device in devices_still_in_outage:
                bruin_client_id = device['cached_info']['bruin_client_info']['client_id']
                serial_number = device['cached_info']['serial_number']

                self._logger.info(f'Attempting outage ticket creation for faulty device {serial_number}...')
                ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                    bruin_client_id, serial_number
                )
                ticket_creation_status = ticket_creation_response['status']
                ticket_id = ticket_creation_response['body']
                if ticket_creation_status in range(200, 300):

                    self._logger.info(f'Outage ticket created for device {serial_number}! Ticket ID: {ticket_id}')
                    slack_message = (
                        f'Outage ticket created for faulty device {serial_number}: https://app.bruin.com/t/{ticket_id}'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)

                    self._logger.info(f'Appending triage note to outage ticket {ticket_id}...')
                    triage_note = self._build_triage_note(device['device_info'])
                    await self._bruin_repository.append_triage_note_to_ticket(ticket_id, serial_number, triage_note)
                elif ticket_creation_status == 409:
                    self._logger.info(
                        f'Faulty device {serial_number} already has an outage ticket in progress (ID = {ticket_id}).'
                    )
                    await self._append_triage_note_if_needed(ticket_id, device['device_info'])
                elif ticket_creation_status == 471:
                    self._logger.info(
                        f'Faulty device {serial_number} has a resolved outage ticket (ID = {ticket_id}). '
                        'Re-opening ticket...'
                    )
                    await self._reopen_outage_ticket(ticket_id, device)
        else:
            self._logger.info(
                "No devices were detected in outage state after re-check. Outage tickets won't be created"
            )

        if healthy_devices:
            self._logger.info(f"{len(healthy_devices)} devices were detected in healthy state after re-check.")
            autoresolve_tasks = [self._run_ticket_autoresolve(device) for device in healthy_devices]
            await asyncio.gather(*autoresolve_tasks)
        else:
            self._logger.info("No devices were detected in healthy state after re-check.")

    async def _append_triage_note_if_needed(self, ticket_id: int, device_info: dict):
        serial_number = device_info['serialNumber']
        self._logger.info(f'Checking ticket {ticket_id} to see if device {serial_number} has a triage note already...')

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        if ticket_details_response['status'] not in range(200, 300):
            return

        ticket_notes = ticket_details_response['body']['ticketNotes']
        relevant_notes = [note for note in ticket_notes if serial_number in note['serviceNumber']]

        if self._triage_note_exists(relevant_notes):
            self._logger.info(
                f'Triage note already exists in ticket {ticket_id} for serial {serial_number}, so no triage '
                f'note will be appended.'
            )
            return

        self._logger.info(
            f'No triage note was found for serial {serial_number} in ticket {ticket_id}. Appending triage note...'
        )
        triage_note = self._build_triage_note(device_info)
        await self._bruin_repository.append_triage_note_to_ticket(ticket_id, serial_number, triage_note)
        self._logger.info(f'Triage note for device {serial_number} appended to ticket {ticket_id}!')

    def _triage_note_exists(self, ticket_notes: list) -> bool:
        triage_note = self._get_first_element_matching(ticket_notes, lambda note: self.__is_triage_note(note))
        return bool(triage_note)

    @staticmethod
    def __is_triage_note(note: dict) -> bool:
        return bool(TRIAGE_NOTE_REGEX.match(note['noteValue']))

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback

    async def _reopen_outage_ticket(self, ticket_id, device):
        self._logger.info(f'Reopening Hawkeye outage ticket {ticket_id}...')

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']
        if ticket_details_response_status not in range(200, 300):
            return

        ticket_detail_for_reopen = self._get_first_element_matching(
            ticket_details_response_body['ticketDetails'],
            lambda detail: detail['detailValue'] == device['cached_info']['serial_number'],
        )

        ticket_reopening_response = await self._bruin_repository.open_ticket(ticket_id,
                                                                             ticket_detail_for_reopen['detailID'])
        ticket_reopening_response_status = ticket_reopening_response['status']

        if ticket_reopening_response_status == 200:
            self._logger.info(
                f'Hawkeye outage ticket {ticket_id} reopening succeeded.')
            slack_message = f'Hawkeye outage ticket {ticket_id} reopened: https://app.bruin.com/t/{ticket_id}'
            await self._notifications_repository.send_slack_message(slack_message)
            outage_causes = self._get_outage_causes_for_reopen_note(device)
            await self._bruin_repository.append_reopening_note_to_ticket(ticket_id,
                                                                         device['cached_info']['serial_number'],
                                                                         outage_causes)

            # Check if this part is necessary
            # self._metrics_repository.increment_tickets_reopened()
        else:
            self._logger.error(
                f'[outage-ticket-creation] Outage ticket {ticket_id} reopening failed.'
            )

    def _get_outage_causes_for_reopen_note(self, device: dict) -> str:
        lines = [
            'Outage cause(s):',
        ]

        node_to_node_status: str = 'DOWN' if device['device_info']['nodetonode']['status'] == 0 else 'UP'
        real_service_status: str = 'DOWN' if device['device_info']['realservice']['status'] == 0 else 'UP'
        if real_service_status == "DOWN":
            lines.append(f'Real service status is {real_service_status}.')
        if node_to_node_status == "DOWN":
            lines.append(f'Node to node status is {node_to_node_status}.')

        return os.linesep.join(lines)

    def _build_triage_note(self, device_info: dict) -> str:
        tz_object = timezone(self._config.MONITOR_CONFIG['timezone'])
        current_datetime = datetime.now(utc).astimezone(tz_object)

        node_to_node_status: str = 'DOWN' if device_info['nodetonode']['status'] == 0 else 'UP'
        real_service_status: str = 'DOWN' if device_info['realservice']['status'] == 0 else 'UP'

        triage_note = os.linesep.join([
            "#*Automation Engine*#",
            "Triage (Ixia)",
            "",
            "Hawkeye Instance: https://ixia.metconnect.net/",
            "Links: [Dashboard|https://ixia.metconnect.net/ixrr_main.php?type=ProbesManagement] - "
            f"[Probe|https://ixia.metconnect.net/probeinformation.php?probeid={device_info['probeId']}]",
            f"Device Name: {device_info['name']}",
            f"Device Type: {device_info['typeName']}",
            f"Serial: {device_info['serialNumber']}",
            f"Device Node to Node Status: {node_to_node_status}",
            f"Node to Node Last Update: {str(parse(device_info['nodetonode']['lastUpdate']).astimezone(tz_object))}",
            f"Device Real Service Status: {real_service_status}",
            f"Real Service Last Update: {str(parse(device_info['realservice']['lastUpdate']).astimezone(tz_object))}",
            "",
            f"TimeStamp: {str(current_datetime)}",
        ])
        return triage_note

    def _was_last_outage_detected_recently(self, ticket_notes: list, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_outage = self._config.MONITOR_CONFIG['autoresolve_last_outage_seconds']

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note['createdDate'])

        last_reopen_note = self._get_last_element_matching(
            notes_sorted_by_date_asc,
            lambda note: REOPEN_NOTE_REGEX.match(note['noteValue'])
        )
        if last_reopen_note:
            note_creation_date = parse(last_reopen_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        triage_note = self._get_first_element_matching(
            notes_sorted_by_date_asc,
            lambda note: TRIAGE_NOTE_REGEX.match(note['noteValue'])
        )
        if triage_note:
            note_creation_date = parse(triage_note['createdDate']).astimezone(utc)
            seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage

        ticket_creation_datetime = parse(ticket_creation_date, ignoretz=True)
        seconds_elapsed_since_last_outage = (current_datetime - ticket_creation_datetime).total_seconds()
        return seconds_elapsed_since_last_outage <= max_seconds_since_last_outage
