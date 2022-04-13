import os
import re
from collections import defaultdict
from datetime import datetime

import asyncio
from dateutil.parser import parse
from pytz import timezone
from shortuuid import uuid
from tenacity import wait_fixed, retry, stop_after_attempt

from application import AffectingTroubles
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
                'product_category': self._config.PRODUCT_CATEGORY,
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
                        f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )
                else:
                    err_msg = (
                        f'Error while retrieving tickets with any status of {ticket_statuses}, with ticket topic '
                        f'{ticket_topic}, service number {service_number} and belonging to client {client_id} in '
                        f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                        f'Error {response_status} - {response_body}'
                    )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )
            else:
                self._logger.info(f'Got details of ticket {ticket_id} from Bruin!')

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)
        return response

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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment. Note was {note}. Error: '
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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment. '
                    f'Error: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def create_affecting_ticket(self, client_id: int, service_number: str, contact_info: list):
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
                "contacts": contact_info
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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
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
                    f'{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} '
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
                    f'{self._config.ENVIRONMENT_NAME.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def post_notification_email_milestone(self, ticket_id: int, service_number: str):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {
                'notification_type': 'TicketBYOBAffectingRepairAcknowledgement-E-Mail',
                'ticket_id': ticket_id,
                'service_number': service_number,
            },
        }

        try:
            self._logger.info(f'Sending email for ticket id {ticket_id} '
                              f'and service_number {service_number}...')
            response = await self._event_bus.rpc_request('bruin.notification.email.milestone', request, timeout=90)
        except Exception as e:
            err_msg = (f'An error occurred when sending email for ticket id {ticket_id} '
                       f'and service_number {service_number}...-> {e}')
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status in range(200, 300):
                self._logger.info(f'Email sent for ticket {ticket_id} and service number {service_number}!')
            else:
                err_msg = (
                    f'Error while sending email for ticket {ticket_id} and '
                    f'service_number {service_number} in '
                    f'{self._config.CURRENT_ENVIRONMENT.upper()} environment: '
                    f'Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def get_contact_info_for_site(site_details):
        site_detail_name = site_details["primaryContactName"]
        site_detail_phone = site_details["primaryContactPhone"]
        site_detail_email = site_details["primaryContactEmail"]

        if site_detail_name is None or site_detail_email is None:
            return None

        contact_info = [
            {
                "email": site_detail_email,
                "name": site_detail_name,
                "type": "ticket",
            },
            {
                "email": site_detail_email,
                "name": site_detail_name,
                "type": "site",
            }
        ]

        if site_detail_phone is not None:
            contact_info[0]["phone"] = site_detail_phone
            contact_info[1]["phone"] = site_detail_phone

        return contact_info

    async def get_affecting_tickets(self, client_id: int, ticket_statuses: list, *, service_number: str = None):
        ticket_topic = 'VAS'

        return await self.get_tickets(client_id, ticket_topic, ticket_statuses, service_number=service_number)

    async def get_open_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['New', 'InProgress', 'Draft']

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def get_resolved_affecting_tickets(self, client_id: int, *, service_number: str = None):
        ticket_statuses = ['Resolved']

        return await self.get_affecting_tickets(client_id, ticket_statuses, service_number=service_number)

    async def change_detail_work_queue_to_hnoc(self, ticket_id: int, *, service_number: str = None):
        task_result = 'HNOC Investigate'

        return await self.change_detail_work_queue(
            ticket_id=ticket_id, task_result=task_result, service_number=service_number
        )

    async def append_autoresolve_note_to_ticket(self, ticket_id: int, serial_number: str):
        all_troubles = list(AffectingTroubles)
        troubles_joint = f"{', '.join(trouble.value for trouble in all_troubles[:-1])} and {all_troubles[-1].value}"

        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))
        autoresolve_note = os.linesep.join([
            "#*MetTel's IPA*#",
            f'All Service Affecting conditions ({troubles_joint}) have stabilized.',
            f'Auto-resolving task for serial: {serial_number}',
            f'TimeStamp: {current_datetime_tz_aware}',
        ])

        return await self.append_note_to_ticket(ticket_id, autoresolve_note, service_numbers=[serial_number])

    # ------------------------ Legacy methods for SA reports ------------------------
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
                    'category': self._config.PRODUCT_CATEGORY,
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

            response = await self.get_all_affecting_tickets(client_id=client_id, start_date=start_date,
                                                            end_date=end_date, ticket_statuses=ticket_statuses)

            if not response:
                return None

            self._logger.info(f"Getting ticket details for {len(response['body'])} tickets")
            all_tickets_sorted = sorted(response['body'], key=lambda item: parse(item['createDate']), reverse=True)
            tasks = [self._get_ticket_details(ticket) for ticket in all_tickets_sorted]
            tickets = await asyncio.gather(*tasks, return_exceptions=True)
            tickets = {ticket['ticket']['ticketID']: ticket for ticket in tickets if ticket}

            return tickets
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
    def group_ticket_details_by_serial_and_interface(ticket_details):
        grouped_tickets = defaultdict(lambda: defaultdict(list))

        for detail in ticket_details:
            serial = detail['ticket_detail']['detailValue']

            for note in detail['ticket_notes']:
                match = INTERFACE_NOTE_REGEX.search(note['noteValue'])

                if match:
                    interface = match['interface_name']
                    grouped_tickets[serial][interface].append(detail)

        return grouped_tickets

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

    def prepare_items_for_monitor_report(self, all_serials, cached_info_by_serial):
        items_for_report = []
        for serial, ticket_details in all_serials.items():
            interfaces_by_trouble = self.search_interfaces_and_count_in_details(ticket_details)
            cached_info = cached_info_by_serial[serial]
            for trouble in interfaces_by_trouble.keys():
                for interface, ticket_ids in interfaces_by_trouble[trouble].items():
                    self._logger.info(f"--> {serial} : {len(ticket_details)} tickets")
                    item_report = self.build_monitor_report_item(ticket_details=ticket_details, cached_info=cached_info,
                                                                 number_of_tickets=len(ticket_ids), interface=interface,
                                                                 trouble=trouble)
                    items_for_report.append(item_report)

        return items_for_report

    @staticmethod
    def build_monitor_report_item(ticket_details, cached_info, number_of_tickets, interface, trouble):
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

    def prepare_items_for_bandwidth_report(self, links_metrics, grouped_ticket_details):
        report_items = []

        for link_metrics in links_metrics:
            serial_number = link_metrics['link']['edgeSerialNumber']
            edge_name = link_metrics['link']['edgeName']
            interface = link_metrics['link']['interface']
            bandwidth = link_metrics['avgBandwidth']
            ticket_details = grouped_ticket_details[serial_number][interface]
            report_item = self.build_bandwidth_report_item(serial_number=serial_number, edge_name=edge_name,
                                                           interface=interface, bandwidth=bandwidth,
                                                           ticket_details=ticket_details)
            report_items.append(report_item)

        return report_items

    @staticmethod
    def build_bandwidth_report_item(serial_number, edge_name, interface, bandwidth, ticket_details):
        return {
            'serial_number': serial_number,
            'edge_name': edge_name,
            'interface': interface,
            'bandwidth': bandwidth,
            'threshold_exceeded': len(ticket_details),
            'ticket_ids': set(detail['ticket_id'] for detail in ticket_details),
        }

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
                    if f'Trouble: {trouble}' in ticket_note["noteValue"]
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

    async def append_asr_forwarding_note(self, ticket_id, link, serial_number):
        current_datetime_tz_aware = datetime.now(timezone(self._config.TIMEZONE))

        note_lines = [
            f"#*MetTel's IPA*#",
            f'Status of Wired Link {link["interface"]} ({link["displayName"]}) is {link["linkState"]}.',
            f'Moving task to: ASR Investigate',
            f'TimeStamp: {current_datetime_tz_aware}',
        ]

        task_result_note = os.linesep.join(note_lines)
        return await self.append_note_to_ticket(ticket_id, task_result_note, service_numbers=[serial_number])
