import csv
import io
import time
from datetime import datetime, timedelta
from typing import Set

import asyncio
from apscheduler.util import undefined
from pytz import timezone


class DiGiRebootReport:

    def __init__(self, event_bus, scheduler, logger, config, bruin_repository, digi_repository,
                 notification_repository, customer_cache_repository):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger
        self._config = config
        self._bruin_repository = bruin_repository
        self._digi_repository = digi_repository
        self._notification_repository = notification_repository
        self._customer_cache_repository = customer_cache_repository

    async def start_digi_reboot_report_job(self, exec_on_start=False):
        self._logger.info(f"Scheduled task: DiGi reboot report process configured to run every "
                          f"{self._config.DIGI_CONFIG['digi_reboot_report_time']/60} hours")
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.DIGI_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._digi_reboot_report_process, 'interval',
                                minutes=self._config.DIGI_CONFIG['digi_reboot_report_time'],
                                next_run_time=next_run_time,
                                replace_existing=False, id='_digi_reboot_report')

    async def _digi_reboot_report_process(self):
        self._logger.info("Starting DiGi reboot report process")
        start = time.time()

        ticket_id_list = await self._get_all_close_service_outage_ticket_ids()
        ticket_task_history_map = await self._get_ticket_task_histories(ticket_id_list)
        await self._merge_recovery_logs(ticket_task_history_map)
        await self._generate_and_email_csv_file(ticket_task_history_map)
        stop = time.time()

        self._logger.info(f'DiGi reboot report process finished in {round((stop - start) / 60, 2)} minutes')

    async def _get_all_close_service_outage_ticket_ids(self):
        self._logger.info('Creating a list of all closed ticket IDS')
        closed_ticket_ids = []

        customer_cache_response = await self._customer_cache_repository.get_cache()
        customer_cache_response_status = customer_cache_response['status']
        if customer_cache_response_status not in range(200, 300) or customer_cache_response_status == 202:
            return []

        customer_cache: list = customer_cache_response['body']
        bruin_clients_ids: Set[int] = set(elem['bruin_client_info']['client_id'] for elem in customer_cache)

        for client_id in bruin_clients_ids:
            await self._get_closed_tickets_by_client_id(client_id, closed_ticket_ids)

        self._logger.info('List of all closed ticket IDS created')
        self._logger.info(closed_ticket_ids)
        return closed_ticket_ids

    async def _get_closed_tickets_by_client_id(self, client_id, closed_ticket_ids):
        closed_outage_tickets_response = await self._bruin_repository.get_closed_tickets(client_id)
        closed_outage_tickets_response_body = closed_outage_tickets_response['body']
        closed_outage_tickets_response_status = closed_outage_tickets_response['status']
        if closed_outage_tickets_response_status not in range(200, 300):
            closed_outage_tickets_response_body = []

        for ticket in closed_outage_tickets_response_body:
            closed_ticket_ids.append(ticket['ticketID'])

    async def _get_ticket_task_histories(self, ticket_id_list):
        ticket_map = {}
        self._logger.info('Creating ticket map of ticket id to ticket task history')
        for ticket_id in ticket_id_list:
            self._logger.info(f'Grabbing the ticket task history for ticket {ticket_id}')
            ticket_task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            ticket_task_history_response_body = ticket_task_history_response["body"]
            ticket_task_history_response_status = ticket_task_history_response["status"]

            if ticket_task_history_response_status not in range(200, 300):
                return ticket_map
            self._logger.info(f'Parsing all data in the ticket task history for ticket {ticket_id}')
            ticket_info = self._parse_ticket_history(ticket_task_history_response_body)

            if ticket_info['reboot_attempted']:
                ticket_map[ticket_id] = ticket_info

        return ticket_map

    def _parse_ticket_history(self, ticket_history):
        ticket_info = {
            'outage_type': None,
            'reboot_attempted': False,
            'reboot_time': None,
            'process_attempted': False,
            'process_successful': False,
            'process_start': None,
            'process_end': None,
            'process_length': None,
            'reboot_method': None,
            'autoresolved': False,
            'autoresolve_time': None,
            'forwarded': False
        }

        for entry in ticket_history:
            if 'NoteType' not in entry or entry['NoteType'] != 'ADN' or entry['Notes'] is None:
                continue

            note = entry['Notes']

            time = entry['EnteredDate_N']
            if ":" == time[-3:-2]:
                time = time[:-3] + time[-2:]

            if '.' not in time:
                note_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
            else:
                note_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z')

            if 'Triage' in entry['Notes']:
                edge_status = self._get_edge_status_from_note(note)

                if edge_status:
                    if edge_status == 'CONNECTED':
                        ticket_info['outage_type'] = 'Link'
                    else:
                        ticket_info['outage_type'] = 'Edge'

            if 'Offline DiGi interface identified' in note:
                ticket_info['process_attempted'] = True
                ticket_info['reboot_time'] = note_time

            if 'DiGi reboot failed' in note:
                ticket_info['forwarded'] = True

            if 'Auto-resolving detail for serial' in note:
                ticket_info['autoresolve_time'] = note_time

        return ticket_info

    def _get_edge_status_from_note(self, text):
        if 'Edge Status' in text:
            index = text.index('Edge Status: ') + 13
            status = ''
            while index < len(text):
                char = text[index]
                if char == '\n':
                    break
                status += char
                index += 1
            return status
        return None

    async def _merge_recovery_logs(self, ticket_map):
        self._logger.info('Grabbing DiGi recovery logs')
        digi_recovery_logs_response = await self._digi_repository.get_digi_recovery_logs()
        digi_recovery_logs_response_body = digi_recovery_logs_response['body']
        digi_recovery_logs_response_status = digi_recovery_logs_response['status']

        if digi_recovery_logs_response_status not in range(200, 300):
            return

        processes = digi_recovery_logs_response_body['Logs']

        for process in processes:

            ticket_id = process['TicketID']

            if ticket_id not in ticket_map:
                continue

            self._logger.info(f'Merging data from DiGi recovery logs of ticket id {ticket_id} '
                              f'into the ticket ID to ticket task history map')

            ticket_map[ticket_id]['process_start'] = datetime.strptime(
                process['TimestampSTART'], '%Y-%m-%dT%H:%M:%SZ') if process['TimestampSTART'] is not None else None
            ticket_map[ticket_id]['process_end'] = datetime.strptime(
                process['TimestampEND'], '%Y-%m-%dT%H:%M:%SZ') if process['TimestampEND'] is not None else None

            if process.get('Success'):
                ticket_map[ticket_id]['process_successful'] = True

            autoresolve_time = ticket_map[ticket_id]['autoresolve_time']

            if ticket_map[ticket_id]['process_end'] is not None:
                ticket_map[ticket_id]['process_length'] = ticket_map[ticket_id]['process_end'] - ticket_map[ticket_id][
                                                                                                        'process_start']

                if autoresolve_time:
                    if ticket_map[ticket_id]['process_end'] <= autoresolve_time < (
                            autoresolve_time + timedelta(minutes=5)):
                        ticket_map[ticket_id]['autoresolved'] = True

            ticket_map[ticket_id]['reboot_method'] = process['Method']

    async def _generate_and_email_csv_file(self, ticket_map):
        self._logger.info('Generating a csv file from the ticket map of ticket IDs to ticket task histories')

        fields = ['Time (UTC)',  # 0
                  'Reboot Request Attempts',  # 1
                  'Edge Outages',  # 2
                  'Link Outages',  # 3
                  'Unclassified Outages',  # 4
                  'Reboot Request Successful',  # 5
                  'DiGi Reboot Process Attempts',  # 6
                  'DiGi Reboot Process Successful',  # 7
                  'Ping Reboots Attempted',  # 8
                  'Ping Reboots Successful',  # 9
                  'OEMPortal Reboots Attempted',  # 10
                  'OEMPortal Reboots Successful',  # 11
                  'SSH Reboots Attempted',  # 12
                  'SSH Reboots Successful',  # 13
                  'SMS Reboots Attempted',  # 14
                  'SMS Reboots Successful',  # 15
                  'API Start Reboots Attempted',  # 16
                  'API Start Reboots Successful',  # 17
                  'Tasks Autoresolved with Reboot Requests',  # 18
                  'Edge Outage Tasks Autoresolved',  # 19
                  'Link Outage Tasks Autoresolved',  # 20
                  'Unclassified Outage Tasks Autoresolved',  # 21
                  'Tasks Forwarded to Wireless',  # 22
                  'Edge Outage Tasks Forwarded',  # 23
                  'Link Outage Tasks Forwarded',  # 24
                  'Unclassified Outage Tasks Forwarded']  # 25

        breakdown = {}

        for ticket_id in ticket_map:
            ticket_info = ticket_map[ticket_id]

            day = ticket_info['reboot_time'].strftime('%m/%d')

            if day not in breakdown:
                breakdown[day] = [day] + ([0] * (len(fields) - 1))

            breakdown[day][1] += 1

            outage_type = ticket_info['outage_type']

            if outage_type == 'Edge':
                breakdown[day][2] += 1
            if outage_type == 'Link':
                breakdown[day][3] += 1
            if outage_type is None:
                breakdown[day][4] += 1

            breakdown[day][5] += 1

            if ticket_info['process_attempted']:
                breakdown[day][6] += 1

            methods = {
                'Ping': 8,
                'OEMPortal': 10,
                'SSH': 12,
                'SMS': 14,
                'API Start': 16,
            }

            method = ticket_info['reboot_method']

            if method is not None:
                breakdown[day][methods[method]] += 1

            process_successful = ticket_info['process_successful']

            if process_successful:
                breakdown[day][7] += 1
                if method is not None:
                    breakdown[day][methods[method] + 1] += 1

            if ticket_info['autoresolved']:
                breakdown[day][18] += 1

                if outage_type == 'Edge':
                    breakdown[day][19] += 1
                if outage_type == 'Link':
                    breakdown[day][20] += 1
                if outage_type is None:
                    breakdown[day][21] += 1

            if ticket_info['forwarded']:
                breakdown[day][22] += 1

                if outage_type == 'Edge':
                    breakdown[day][23] += 1
                if outage_type == 'Link':
                    breakdown[day][24] += 1
                if outage_type is None:
                    breakdown[day][25] += 1

        days = list(breakdown.keys())
        days.sort()

        filename = 'digi_recovery_report.csv'

        with open(filename, 'w'):
            buf = io.StringIO()
            csvwriter = csv.writer(buf)
            csvwriter.writerow(fields)
            for day in days:
                csvwriter.writerow(breakdown[day])
            buf.seek(0)
            raw_csv = buf.read()
            self._logger.info('Sending csv file through email')
            await self._notification_repository.send_email(raw_csv)
