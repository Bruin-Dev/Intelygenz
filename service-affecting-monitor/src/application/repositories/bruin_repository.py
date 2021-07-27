import os
import re
from collections import defaultdict
from datetime import datetime

import asyncio
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid
from tenacity import wait_fixed, retry, stop_after_attempt

from application.repositories import nats_error_response

INTERFACE_NOTE_REGEX = re.compile(r'Interface: (?P<interface_name>[a-zA-Z0-9]+)')


class BruinRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_REPORT_CONFIG["semaphore"])

    async def get_tickets(self, client_id: int, ticket_topic: str, ticket_statuses: list, *,
                          service_number: str = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_statuses': ticket_statuses,
                'ticket_topic': ticket_topic,
                'product_category': 'SD-WAN',
            },
        }

        if service_number:
            request['body']['service_number'] = service_number

        try:
            if not service_number:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses}, with ticket topic '
                    f'{ticket_topic} and belonging to client {client_id} from Bruin...'
                )
            else:
                self._logger.info(
                    f'Getting all tickets with any status of {ticket_statuses}, with ticket topic '
                    f'{ticket_topic}, service number {service_number} and belonging to client {client_id} from Bruin...'
                )

            response = await self._event_bus.rpc_request("bruin.ticket.basic.request", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting tickets from Bruin API with any status of {ticket_statuses}, '
                f'with ticket topic {ticket_topic} and belonging to client {client_id} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                if not service_number:
                    self._logger.info(
                        f'Got all tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic} and belonging to client {client_id} from Bruin!'
                    )
                else:
                    self._logger.info(
                        f'Got all tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client '
                        f'{client_id} from Bruin!'
                    )
            else:
                if not service_number:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic} and belonging to client {client_id} in '
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client {client_id} in '
                        f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_affecting_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VAS'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def append_note_to_ticket(self, ticket_id: int, note: str, *, service_numbers: list = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': note,
            },
        }

        if service_numbers:
            request['body']['service_numbers'] = service_numbers

        try:
            self._logger.info(f'Appending note to ticket {ticket_id}... Note contents: {note}')
            response = await self._event_bus.rpc_request("bruin.ticket.note.append.request", request, timeout=15)
            self._logger.info(f'Note appended to ticket {ticket_id}!')
        except Exception as e:
            err_msg = (
                f'An error occurred when appending a ticket note to ticket {ticket_id}. '
                f'Ticket note: {note}. Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while appending note to ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment. Note was {note}. Error: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def unpause_ticket_detail(self, ticket_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
                "service_number": service_number,
            },
        }

        try:
            self._logger.info(f'Unpausing detail of ticket {ticket_id} related to serial number {service_number}...')
            response = await self._event_bus.rpc_request("bruin.ticket.unpause", request, timeout=30)
        except Exception as e:
            err_msg = (
                f'An error occurred when unpausing detail of ticket {ticket_id} related to serial number '
                f'{service_number}. Error: {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Detail of ticket {ticket_id} related to serial number {service_number}) was unpaused!'
                )
            else:
                err_msg = (
                    f'Error while unpausing detail of ticket {ticket_id} related to serial number {service_number}) in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment. '
                    f'Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_affecting_ticket(self, client_id: int, service_number: str, contact_info: dict):
        err_msg = None
        ticket_details = {
            "request_id": uuid(),
            "body": {
                "clientId": client_id,
                "category": "VAS",
                "services": [
                    {
                        "serviceNumber": service_number
                    }
                ],
                "contacts": [
                    {
                        "email": contact_info['site']['email'],
                        "phone": contact_info['site']['phone'],
                        "name": contact_info['site']['name'],
                        "type": "site"
                    },
                    {
                        "email": contact_info['ticket']['email'],
                        "phone": contact_info['ticket']['phone'],
                        "name": contact_info['ticket']['name'],
                        "type": "ticket"
                    }
                ]
            }
        }

        try:
            self._logger.info(
                f'Creating affecting ticket for serial {service_number} belonging to client {client_id}...')

            response = await self._event_bus.rpc_request("bruin.ticket.creation.request",
                                                         ticket_details, timeout=90)

        except Exception as e:
            err_msg = (
                f'An error occurred while creating affecting ticket for client id {client_id} and serial '
                f'{service_number} -> {e}')
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Affecting ticket for client {client_id} and serial {service_number} created successfully!')
            else:
                err_msg = (
                    f'Error while opening affecting ticket for client {client_id} and serial {service_number} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def open_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        try:
            self._logger.info(f'Opening ticket {ticket_id} (affected detail ID: {detail_id})...')
            response = await self._event_bus.rpc_request("bruin.ticket.status.open", request, timeout=15)
            self._logger.info(f'Ticket {ticket_id} opened!')
        except Exception as e:
            err_msg = f'An error occurred when opening outage ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while opening outage ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue(self, ticket_id: int, task_result: str, *, service_number: str = None,
                                       detail_id: int = None):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                "ticket_id": ticket_id,
                "queue_name": task_result
            },
        }

        if service_number:
            request['body']["service_number"] = service_number

        if detail_id:
            request['body']["detail_id"] = detail_id

        try:
            self._logger.info(
                f'Changing task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} '
                f'to {task_result}...'
            )
            response = await self._event_bus.rpc_request("bruin.ticket.change.work", request, timeout=90)
        except Exception as e:
            err_msg = (
                f'An error occurred when changing task result of detail {detail_id} / serial {service_number} '
                f'in ticket {ticket_id} to {task_result} -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(
                    f'Task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} '
                    f'changed to {task_result} successfully!'
                )
            else:
                err_msg = (
                    f'Error while changing task result of detail {detail_id} / serial {service_number} in ticket '
                    f'{ticket_id} to {task_result} in {self._config.MONITOR_CONFIG["environment"].upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def resolve_ticket(self, ticket_id: int, detail_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        try:
            self._logger.info(f'Resolving detail {detail_id} of ticket {ticket_id}...')
            response = await self._event_bus.rpc_request("bruin.ticket.status.resolve", request, timeout=15)
        except Exception as e:
            err_msg = f'An error occurred while resolving detail {detail_id} of ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Detail {detail_id} of ticket {ticket_id} resolved successfully!')
            else:
                err_msg = (
                    f'Error while resolving detail {detail_id} of ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def change_detail_work_queue_to_hnoc(self, ticket_id: int, *, service_number: str = None,
                                               detail_id: int = None):
        task_result = 'HNOC Investigate'

        return await self.change_detail_work_queue(
            ticket_id=ticket_id, task_result=task_result, service_number=service_number, detail_id=detail_id
        )

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        autoresolve_note = os.linesep.join([
            "#*MetTel's IPA*#",
            'All Service Affecting conditions (Jitter, Packet Loss, Latency and Utilization) have stabilized.',
            f'Auto-resolving task for serial: {serial_number}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, autoresolve_note, service_numbers=[serial_number])

    async def append_reopening_note_to_ticket(self, ticket_id: int, affecting_causes: str):
        current_datetime_tz_aware = datetime.now(timezone(self._config.MONITOR_CONFIG['timezone']))
        reopening_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Re-opening ticket.',
            f'{affecting_causes}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, reopening_note)

    async def get_affecting_ticket(self, client_id, serial):
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved']
        ticket_request_msg = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'product_category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'service_number': serial,
                'ticket_statuses': ticket_statuses
            }
        }
        self._logger.info(f"Retrieving affecting tickets for serial: {serial}")
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.basic.request",
                                                        ticket_request_msg,
                                                        timeout=90)
        if all_tickets['status'] not in range(200, 300):
            self._logger.error(f"Error: an error occurred retrieving affecting tickets by serial")
            return None

        if len(all_tickets['body']) > 0:
            all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]), reverse=True)
            ticket_id = all_tickets_sorted[0]['ticketID']
            ticket_details = await self.get_ticket_details(ticket_id)

            if ticket_details['status'] not in range(200, 300):
                self._logger.error(f"Error: an error occurred retrieving ticket details for ticket: {ticket_id}")
                return None

            ticket_details_body = ticket_details['body']
            self._logger.info(f'Returning ticket details of ticket: {ticket_id}')
            return {
                'ticketID': ticket_id,
                **ticket_details_body,
            }
        self._logger.info(f'No service affecting tickets found for serial: {serial}')
        return {}

    async def get_ticket_details(self, ticket_id: int):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id
            },
        }

        try:
            self._logger.info(f'Getting details of ticket {ticket_id} from Bruin...')
            response = await self._event_bus.rpc_request("bruin.ticket.details.request", request, timeout=15)
        except Exception as e:
            err_msg = f'An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving details of ticket {ticket_id} in '
                    f'{self._config.MONITOR_CONFIG["environment"].upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
        return response

    async def _get_ticket_details(self, ticket):
        @retry(wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG['wait_fixed']),
               stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG['stop_after_attempt']),
               reraise=True)
        async def _get_ticket_details():
            async with self._semaphore:
                ticket_id = ticket['ticketID']
                ticket_details = await self.get_ticket_details(ticket_id)
                if ticket_details['status'] in [401, 403]:
                    self._logger.exception(f"Error: Retry after few seconds. Status: {ticket_details['status']}")
                    raise Exception(f"Error: Retry after few seconds. Status: {ticket_details['status']}")

                if ticket_details['status'] not in range(200, 300):
                    self._logger.error(f"Error: an error occurred retrieving ticket details for ticket: {ticket_id}")
                    return None

                ticket_details_body = ticket_details['body']
                self._logger.info(f'Returning ticket details of ticket: {ticket_id}')
                return {
                    "ticket": ticket,
                    "ticket_details": ticket_details_body
                }

        try:
            return await _get_ticket_details()
        except Exception as e:
            msg = f"[service-affecting-monitor-reports]" \
                  f"Max retries reached getting ticket details {ticket['ticketID']}"
            self._logger.error(msg)
            await self._notifications_repository.send_slack_message(msg)
            return None

    async def get_all_affecting_tickets(self, client_id=None, serial=None, start_date=None, end_date=None,
                                        ticket_statuses=None):
        @retry(wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG['wait_fixed']),
               stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG['stop_after_attempt']),
               reraise=True)
        async def _get_all_affecting_tickets():
            ticket_request_msg = {
                'request_id': uuid(),
                'body': {
                    'client_id': client_id,
                    'category': 'SD-WAN',
                    'ticket_topic': 'VAS',
                    'ticket_status': ticket_statuses
                }
            }
            if start_date:
                ticket_request_msg['body']['start_date'] = start_date
            if end_date:
                ticket_request_msg['body']['end_date'] = end_date
            if serial:
                ticket_request_msg['body']['service_number'] = serial

            response_all_tickets = await self._event_bus.rpc_request("bruin.ticket.request", ticket_request_msg,
                                                                     timeout=90)

            if response_all_tickets['status'] in [401, 403]:
                self._logger.exception(
                    f"Error: Retry after few seconds all tickets. Status: {response_all_tickets['status']}")
                raise Exception(f"Error: Retry after few seconds all tickets. Status: {response_all_tickets['status']}")

            if response_all_tickets['status'] not in range(200, 300):
                self._logger.error(f"Error: an error occurred retrieving affecting tickets")
                return None
            return response_all_tickets

        try:
            return await _get_all_affecting_tickets()
        except Exception as e:
            msg = f"Max retries reached getting all tickets for the service affecting monitor process."
            self._logger.error(f"{msg} - exception: {e}")
            await self._notifications_repository.send_slack_message(msg)
            return None

    async def get_affecting_ticket_for_report(self, client_id, start_date, end_date):
        @retry(wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG['wait_fixed']),
               stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG['stop_after_attempt']),
               reraise=True)
        async def get_affecting_ticket_for_report():
            ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']

            self._logger.info(f"Retrieving affecting tickets between start date: {start_date} and end date: {end_date}")

            all_tickets = await self.get_all_affecting_tickets(client_id=client_id, start_date=start_date,
                                                               end_date=end_date, ticket_statuses=ticket_statuses)

            if all_tickets and len(all_tickets['body']) > 0:
                self._logger.info(f"Getting ticket {len(all_tickets['body'])} details")
                all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]),
                                            reverse=True)
                tasks = [self._get_ticket_details(ticket) for ticket in all_tickets_sorted]
                ret_tickets = await asyncio.gather(*tasks, return_exceptions=True)
                ret_tickets = {ticket['ticket']['ticketID']: ticket for ticket in ret_tickets if ticket}

                return ret_tickets
            return None
        try:
            return await get_affecting_ticket_for_report()
        except Exception as e:
            msg = f"[service-affecting-monitor-reports] Max retries reached getting all tickets for the report."
            self._logger.error(f"{msg} - exception: {e}")
            await self._notifications_repository.send_slack_message(msg)
            return None

    def group_ticket_details_by_serial(self, tickets):
        all_serials = defaultdict(list)

        self._logger.info(f"[bruin_repository] processing {len(tickets)}")

        for detail_object in tickets:
            self._logger.info(f"[bruin_repository] ticket_id: {detail_object['ticket_id']}")
            serial = detail_object['ticket_detail']['detailValue'].upper()
            all_serials[serial].append(detail_object)
        return all_serials

    @staticmethod
    def search_interfaces_in_details(ticket_details):
        interfaces = set()
        for detail_object in ticket_details:
            for note in detail_object['ticket_notes']:
                interface = INTERFACE_NOTE_REGEX.search(note['noteValue'])
                if interface:
                    interfaces.add(interface['interface_name'])
        return list(interfaces)

    @staticmethod
    def search_interfaces_and_count_in_details(ticket_details):
        interfaces_by_trouble = dict()
        for detail_object in ticket_details:
            for note in detail_object['ticket_notes']:
                interface = INTERFACE_NOTE_REGEX.search(note['noteValue'])
                if interface:
                    trouble = detail_object['trouble_value']
                    interface_name = interface['interface_name']
                    interfaces_by_trouble.setdefault(trouble, {})
                    interfaces_by_trouble[trouble].setdefault(interface_name, set())
                    interfaces_by_trouble[trouble][interface_name].add(detail_object['ticket_id'])
        return interfaces_by_trouble

    @staticmethod
    def transform_tickets_into_ticket_details(tickets: dict) -> list:
        result = []
        for ticket_id, ticket_details in tickets.items():
            details = ticket_details['ticket_details']['ticketDetails']
            notes = ticket_details['ticket_details']['ticketNotes']
            ticket = ticket_details['ticket']
            for detail in details:
                serial_number = detail['detailValue']
                notes_related_to_serial = [
                    note
                    for note in notes
                    if serial_number in note['serviceNumber']
                ]
                result.append({
                    'ticket_id': ticket_id,
                    'ticket': ticket,
                    'ticket_detail': detail,
                    'ticket_notes': notes_related_to_serial,
                })
        return result

    def prepare_items_for_report(self, all_serials, cached_info_by_serial):
        items_for_report = []
        bandwidth_config = self._config.MONITOR_REPORT_CONFIG['report_config_by_trouble']['bandwidth']
        for serial, ticket_details in all_serials.items():
            interfaces_by_trouble = self.search_interfaces_and_count_in_details(ticket_details)
            cached_info = cached_info_by_serial[serial]
            client_id = ticket_details[0]['ticket']['clientID']
            for trouble in interfaces_by_trouble.keys():
                for interface, ticket_ids in interfaces_by_trouble[trouble].items():
                    self._logger.info(f"--> {serial} : {len(ticket_details)} tickets")
                    item_report = self.build_item_report(ticket_details=ticket_details, cached_info=cached_info,
                                                         number_of_tickets=len(ticket_ids),
                                                         interface=interface, trouble=trouble)
                    if trouble != 'Bandwidth Over Utilization' or \
                            (client_id in bandwidth_config['client_ids'] and trouble == 'Bandwidth Over Utilization'):
                        items_for_report.append(item_report)

        return items_for_report

    @staticmethod
    def build_item_report(ticket_details, cached_info, number_of_tickets, interface, trouble):
        return {
            'customer': {
                'client_id': ticket_details[0]['ticket']['clientID'],
                'client_name': ticket_details[0]['ticket']['clientName'],
            },
            'location': ticket_details[0]['ticket']['address'],
            'edge_name': cached_info.get('edge_name'),
            'serial_number': cached_info['serial_number'],
            'number_of_tickets': number_of_tickets,
            'bruin_tickets_id': set(
                detail_object['ticket_id']
                for detail_object in ticket_details
            ),
            'interfaces': interface,
            'trouble': trouble
        }

    @staticmethod
    def find_detail_by_serial(ticket, edge_serial_number):
        ticket_details = None
        for detail in ticket.get("ticketDetails"):
            if edge_serial_number == detail['detailValue']:
                ticket_details = detail
                break
        return ticket_details

    @staticmethod
    def filter_ticket_details_by_serials(ticket_details, list_cache_serials):
        return [
            detail_object
            for detail_object in ticket_details
            if detail_object['ticket_detail']['detailValue'] in list_cache_serials
        ]

    @staticmethod
    def filter_trouble_notes_in_ticket_details(tickets_details, troubles):
        ret = []
        for detail_object in tickets_details:
            for trouble in troubles:
                trouble_notes = [
                    ticket_note
                    for ticket_note in detail_object['ticket_notes']
                    if ticket_note["noteValue"]
                    if ('#*Automation Engine*#' in ticket_note["noteValue"] or "#*MetTel's IPA*#" in
                        ticket_note["noteValue"])
                    if trouble in ticket_note["noteValue"]
                ]

                if trouble_notes:
                    ret.append({
                        'ticket_id': detail_object['ticket_id'],
                        'ticket': detail_object['ticket'],
                        'ticket_detail': detail_object['ticket_detail'],
                        'ticket_notes': trouble_notes,
                        'trouble_value': trouble,
                    })
        return ret

    @staticmethod
    def filter_trouble_reports(report_list, active_reports, threshold):
        filter_reports = []
        for report in report_list:
            if report['trouble'] in active_reports and report['number_of_tickets'] >= threshold:
                filter_reports.append(report)
        return filter_reports
