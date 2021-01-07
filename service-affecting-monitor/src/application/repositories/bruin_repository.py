import math
import asyncio
import os
import copy
from datetime import datetime
from dateutil.parser import parse
from collections import defaultdict
from pytz import timezone
from shortuuid import uuid

from application.repositories import nats_error_response


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
            f'#*Automation Engine*#',
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
        async with self._semaphore:
            ticket_id = ticket['ticketID']
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
                "ticket": ticket,
                "ticket_details": ticket_details_body
            }

    async def get_affecting_ticket_for_report(self, report, start_date, end_date):
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

        if all_tickets['status'] not in range(200, 300):
            self._logger.error(f"Error: an error occurred retrieving affecting tickets for report")
            return None

        if len(all_tickets['body']) > 0:
            self._logger.info(f"Getting ticket {len(all_tickets['body'])} details")
            all_tickets_sorted = sorted(all_tickets['body'], key=lambda item: parse(item["createDate"]), reverse=True)
            tasks = [self._get_ticket_details(ticket) for ticket in all_tickets_sorted]
            ret_tickets = await asyncio.gather(*tasks, return_exceptions=True)
            ret_tickets = {ticket['ticket']['ticketID']: ticket for ticket in ret_tickets if ticket}

            return ret_tickets
        self._logger.info(f"No service affecting tickets found for trailing days: {report['trailing_days']}")
        return {}

    def map_tickets_with_serial_numbers(self, tickets):
        all_serials = defaultdict(list)

        self._logger.info(f"[bruin_repository] processing {len(tickets.keys())}")

        for ticket_id, ticket_data in tickets.items():
            self._logger.info(f"[bruin_repository] ticket_id: {ticket_id}")
            serials = list({td['detailValue'].upper() for td in ticket_data['ticket_details']['ticketDetails']})
            for serial in serials:
                all_serials[serial].append(ticket_data)
        return all_serials

    def prepare_items_for_report(self, all_serials):
        items_for_report = []

        for serial, tickets in all_serials.items():
            self._logger.info(f"--> {serial} : {len(tickets)} tickets")
            item_report = {
                'customer': dict(),
                'location': None,
                'serial_number': serial,
                'number_of_tickets': len(tickets),
                'bruin_tickets_id': [],
            }
            only_first_time = True
            for ticket_data in tickets:
                ticket = ticket_data['ticket']
                if only_first_time:
                    only_first_time = False
                    item_report['customer'] = {
                        'client_id': ticket['clientID'],
                        'client_name': ticket['clientName']
                    }
                    item_report['location'] = ticket['address']
                item_report['bruin_tickets_id'].append(ticket['ticketID'])
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
    def find_bandwidth_over_utilization_tickets(tickets, watermark):
        trouble = "Bandwidth Over Utilization"
        ret = {}
        for ticket_id, ticket_details in tickets.items():
            if 'ticketNotes' in ticket_details['ticket_details']:
                for ticket_note in ticket_details['ticket_details']['ticketNotes']:
                    if "noteValue" in ticket_note and ticket_note["noteValue"] and \
                            watermark in ticket_note["noteValue"] and trouble in ticket_note["noteValue"]:
                        ret[ticket_id] = tickets[ticket_id]
        return ret
