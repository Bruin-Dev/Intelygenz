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
            self._logger.info(f"{len(healthy_devices)} devices were detected in healthy state.")
        else:
            self._logger.info("No devices were detected in healthy state.")

        stop = time.time()
        self._logger.info(f'Hawkeye Outage Monitor process finished! Took {round((stop - start) / 60, 2)} minutes')

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

                if ticket_creation_response['status'] in range(200, 300):
                    ticket_id = ticket_creation_response['body']

                    self._logger.info(f'Outage ticket created for device {serial_number}! Ticket ID: {ticket_id}')
                    slack_message = (
                        f'Outage ticket created for faulty device {serial_number}: https://app.bruin.com/t/{ticket_id}'
                    )
                    await self._notifications_repository.send_slack_message(slack_message)

                    self._logger.info(f'Appending triage note to outage ticket {ticket_id}...')
                    triage_note = self._build_triage_note(device['device_info'])
                    await self._bruin_repository.append_triage_note_to_ticket(ticket_id, serial_number, triage_note)
                elif ticket_creation_response['status'] == 409:
                    ticket_id = ticket_creation_response['body']
                    self._logger.info(
                        f'Faulty device {serial_number} already has an outage ticket in progress (ID = {ticket_id}).'
                    )
                    await self._append_triage_note_if_needed(ticket_id, device['device_info'])
                elif ticket_creation_response['status'] == 471:
                    ticket_id = ticket_creation_response['body']
                    self._logger.info(
                        f'Faulty device {serial_number} has a resolved outage ticket (ID = {ticket_id}). '
                        'Skipping outage ticket creation for this device...'
                    )
        else:
            self._logger.info(
                "No devices were detected in outage state after re-check. Outage tickets won't be created"
            )

        if healthy_devices:
            self._logger.info(f"{len(healthy_devices)} devices were detected in healthy state after re-check.")
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
