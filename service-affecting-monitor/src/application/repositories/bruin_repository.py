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

    async def append_note_to_ticket(self, ticket_id: int, note: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': note,
            },
        }

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
                'category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'service_number': serial,
                'ticket_status': ticket_statuses
            }
        }
        self._logger.info(f"Retrieving affecting tickets for serial: {serial}")
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        ticket_request_msg,
                                                        timeout=90)
        if all_tickets['status'] not in range(200, 300):
            self._logger.error(f"Error: an error occurred retrieving affecting tickets by serial")
            return None

        if len(all_tickets['body']) > 0:
            all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]), reverse=True)
            ticket_id = all_tickets_sorted[0]['ticketID']
            ticket_details_request = {'request_id': uuid(), 'body': {'ticket_id': ticket_id}}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               ticket_details_request,
                                                               timeout=15)

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

    async def _get_ticket_details(self, ticket):
        @retry(wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG['wait_fixed']),
               stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG['stop_after_attempt']),
               reraise=True)
        async def _get_ticket_details():
            async with self._semaphore:
                ticket_id = ticket['ticketID']
                ticket_details_request = {'request_id': uuid(), 'body': {'ticket_id': ticket_id}}
                ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                                   ticket_details_request,
                                                                   timeout=15)
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

    async def get_affecting_ticket_for_report(self, report, start_date, end_date):
        @retry(wait=wait_fixed(self._config.MONITOR_REPORT_CONFIG['wait_fixed']),
               stop=stop_after_attempt(self._config.MONITOR_REPORT_CONFIG['stop_after_attempt']),
               reraise=True)
        async def get_affecting_ticket_for_report():
            ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']
            ticket_request_msg = {
                'request_id': uuid(),
                'body': {
                    'client_id': report['client_id'],
                    'category': 'SD-WAN',
                    'ticket_topic': 'VAS',
                    'start_date': start_date,
                    'end_date': end_date,
                    'ticket_status': ticket_statuses
                }
            }

            self._logger.info(f"Retrieving affecting tickets for trailing days: {report['trailing_days']}")

            all_tickets = await self._event_bus.rpc_request("bruin.ticket.request", ticket_request_msg, timeout=90)

            if all_tickets['status'] in [401, 403]:
                self._logger.exception(f"Error: Retry after few seconds all tickets. Status: {all_tickets['status']}")
                raise Exception(f"Error: Retry after few seconds all tickets. Status: {all_tickets['status']}")

            if all_tickets['status'] not in range(200, 300):
                self._logger.error(f"Error: an error occurred retrieving affecting tickets for report")
                return None

            if len(all_tickets['body']) > 0:
                self._logger.info(f"Getting ticket {len(all_tickets['body'])} details")
                all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]),
                                            reverse=True)
                tasks = [self._get_ticket_details(ticket) for ticket in all_tickets_sorted]
                ret_tickets = await asyncio.gather(*tasks, return_exceptions=True)
                ret_tickets = {ticket['ticket']['ticketID']: ticket for ticket in ret_tickets if ticket}

                return ret_tickets
            self._logger.info(f"No service affecting tickets found for trailing days: {report['trailing_days']}")
            return {}

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
        interfaces = dict()
        for detail_object in ticket_details:
            for note in detail_object['ticket_notes']:
                interface = INTERFACE_NOTE_REGEX.search(note['noteValue'])
                if interface:
                    if interface['interface_name'] in interfaces:
                        interfaces[interface['interface_name']] += 1
                    else:
                        interfaces[interface['interface_name']] = 0
        return interfaces

    @staticmethod
    def transform_tickets_into_ticket_details(tickets: dict) -> list:
        result = []
        for ticket_id, ticket_details in tickets.items():
            ticket_id = ticket_id
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

    def prepare_items_for_report(self, all_serials):
        items_for_report = []

        for serial, ticket_details in all_serials.items():
            self._logger.info(f"--> {serial} : {len(ticket_details)} tickets")
            item_report = {
                'customer': {
                    'client_id': ticket_details[0]['ticket']['clientID'],
                    'client_name': ticket_details[0]['ticket']['clientName'],
                },
                'location': ticket_details[0]['ticket']['address'],
                'serial_number': serial,
                'number_of_tickets': len(ticket_details),
                'bruin_tickets_id': set(
                    detail_object['ticket_id']
                    for detail_object in ticket_details
                ),
                'interfaces': self.search_interfaces_in_details(ticket_details)
            }
            items_for_report.append(item_report)

        return items_for_report

    def prepare_items_for_report_by_interface(self, all_serials):
        items_for_report = []

        for serial, ticket_details in all_serials.items():
            interfaces = self.search_interfaces_and_count_in_details(ticket_details)
            for interface, number_of_tickets in interfaces.items():
                self._logger.info(f"--> {serial} : {len(ticket_details)} tickets")
                item_report = {
                    'customer': {
                        'client_id': ticket_details[0]['ticket']['clientID'],
                        'client_name': ticket_details[0]['ticket']['clientName'],
                    },
                    'location': ticket_details[0]['ticket']['address'],
                    'serial_number': serial,
                    'number_of_tickets': number_of_tickets,
                    'bruin_tickets_id': set(
                        detail_object['ticket_id']
                        for detail_object in ticket_details
                    ),
                    'interfaces': interface
                }
                items_for_report.append(item_report)

        return items_for_report

    @staticmethod
    def find_detail_by_serial(ticket, edge_serial_number):
        ticket_details = None
        for detail in ticket.get("ticketDetails"):
            if edge_serial_number == detail['detailValue']:
                ticket_details = detail
                break
        return ticket_details

    @staticmethod
    def filter_tickets_with_serial_cached(ticket_details, list_cache_serials):
        return [
            detail_object
            for detail_object in ticket_details
            if detail_object['ticket_detail']['detailValue'] in list_cache_serials
        ]

    @staticmethod
    def filter_trouble_notes(tickets_details, trouble):
        ret = []
        for detail_object in tickets_details:
            bandwidth_notes = [
                note
                for note in detail_object['ticket_notes']
                if note["noteValue"]
                if ('#*Automation Engine*#' in note["noteValue"] or "#*MetTel's IPA*#" in note["noteValue"])
                if trouble in note["noteValue"]
            ]

            if bandwidth_notes:
                ret.append({
                    'ticket_id': detail_object['ticket_id'],
                    'ticket': detail_object['ticket'],
                    'ticket_detail': detail_object['ticket_detail'],
                    'ticket_notes': bandwidth_notes,
                })
        return ret
