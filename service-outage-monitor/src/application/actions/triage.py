import asyncio
import os
import re
from collections import ChainMap
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import List
from typing import NoReturn

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone
from pytz import utc
from shortuuid import uuid
from igz.packages.eventbus.eventbus import EventBus

from application.repositories.edge_redis_repository import EdgeIdentifier


empty_str = str()


class Triage:
    __client_id_regex = re.compile(r'^.*\|(?P<client_id>\d+)\|$')
    __triage_note_regex = re.compile(r'#\*Automation Engine\*#\nTriage')
    __event_interface_name_regex = re.compile(
        r'(^Interface (?P<interface_name>[a-zA-Z0-9]+) is (up|down)$)|'
        r'(^Link (?P<interface_name2>[a-zA-Z0-9]+) is (no longer|now) DEAD$)'
    )

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, outage_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._outage_repository = outage_repository

    async def start_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every '
                          f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                minutes=self._config.TRIAGE_CONFIG["polling_minutes"],
                                next_run_time=next_run_time,
                                replace_existing=True, id='_triage_process')

    async def _run_tickets_polling(self):
        monitoring_mapping = await self._map_bruin_client_ids_to_edges_serials_and_statuses()

        clients_under_monitoring: List[int] = list(monitoring_mapping.keys())
        open_tickets = await self._get_all_open_tickets_with_details_for_monitored_companies(clients_under_monitoring)

        serials_under_monitoring: List[str] = sum(
            (list(edge_status_by_serial_dict.keys()) for edge_status_by_serial_dict in monitoring_mapping.values()),
            []
        )
        relevant_open_tickets = self._filter_tickets_related_to_edges_under_monitoring(
            open_tickets, serials_under_monitoring
        )

        tickets_with_triage, tickets_without_triage = self._distinguish_tickets_with_and_without_triage(
            relevant_open_tickets)

        edges_data_by_serial = ChainMap(*monitoring_mapping.values())
        await asyncio.gather(
            self._process_tickets_with_triage(tickets_with_triage, edges_data_by_serial),
            self._process_tickets_without_triage(tickets_without_triage, edges_data_by_serial),
        )

    async def _map_bruin_client_ids_to_edges_serials_and_statuses(self):
        mapping = {}

        try:
            edge_list_response = await self._get_edges_for_triage_monitoring()
        except Exception:
            await self._notify_failing_rpc_request_for_edge_list()
            raise

        edge_list_response_body = edge_list_response['body']
        edge_list_response_status = edge_list_response['status']

        if edge_list_response_status not in range(200, 300):
            await self._notify_http_error_when_requesting_edge_list_from_velocloud(edge_list_response)
            raise Exception

        for edge_full_id in edge_list_response_body:
            edge_identifier = EdgeIdentifier(**edge_full_id)

            try:
                edge_status_response = await self._get_edge_status_by_id(edge_full_id)
            except Exception:
                await self._notify_failing_rpc_request_for_edge_status(edge_full_id)
                continue

            edge_status_response_body = edge_status_response['body']
            edge_status_response_status = edge_status_response['status']

            if edge_status_response_status not in range(200, 300):
                await self._notify_http_error_when_requesting_edge_status_from_velocloud(
                    edge_full_id, edge_status_response
                )
                continue

            edge_status_data = edge_status_response_body['edge_info']

            serial_number = edge_status_data['edges']['serialNumber']
            if not serial_number:
                self._logger.info(
                    f"[map-bruin-client-to-edges] Edge {edge_identifier} doesn't have any serial associated. "
                    'Skipping...')
                continue

            enterprise_name = edge_status_data['enterprise_name']
            bruin_client_id = self._extract_client_id(enterprise_name)

            mapping.setdefault(bruin_client_id, {})
            mapping[bruin_client_id][serial_number] = {
                'edge_id': edge_full_id,
                'edge_status': edge_status_data,
            }

        return mapping

    async def _get_edges_for_triage_monitoring(self):
        edge_list_request = {
            "request_id": uuid(),
            "body": {
                'filter': self._config.TRIAGE_CONFIG['velo_filter'],
            },
        }

        edge_list = await self._event_bus.rpc_request("edge.list.request", edge_list_request, timeout=600)
        return edge_list

    async def _notify_failing_rpc_request_for_edge_list(self):
        err_msg = 'An error occurred when requesting edge list from Velocloud'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_edge_list_from_velocloud(self, edge_list_response):
        edge_list_response_body = edge_list_response['body']
        edge_list_response_status = edge_list_response['status']

        err_msg = (
            f'Error while retrieving edge list in {self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
            f'Error {edge_list_response_status} - {edge_list_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _get_edge_status_by_id(self, edge_full_id):
        edge_list_request = {
            "request_id": uuid(),
            "body": edge_full_id,
        }

        edge_list = await self._event_bus.rpc_request("edge.status.request", edge_list_request, timeout=120)
        return edge_list

    async def _notify_failing_rpc_request_for_edge_status(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        err_msg = f'An error occurred when requesting edge status from Velocloud for edge {edge_identifier}'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_edge_status_from_velocloud(self, edge_full_id, edge_status_response):
        edge_status_response_body = edge_status_response['body']
        edge_status_response_status = edge_status_response['status']

        edge_identifier = EdgeIdentifier(**edge_full_id)
        err_msg = (
            f'Error while retrieving edge status for edge {edge_identifier} in '
            f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
            f'Error {edge_status_response_status} - {edge_status_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _get_all_open_tickets_with_details_for_monitored_companies(self, bruin_clients_ids):
        open_tickets = []

        for client_id in bruin_clients_ids:
            try:
                open_tickets += await self._get_open_tickets_with_details_by_client_id(client_id)
            except Exception:
                continue

        return open_tickets

    async def _get_open_tickets_with_details_by_client_id(self, client_id):
        result = []

        try:
            open_tickets_response = await self._get_open_tickets_by_client_id(client_id)
        except Exception:
            await self._notify_failing_rpc_request_for_open_tickets(client_id)
            raise

        open_tickets_response_body = open_tickets_response['body']
        open_tickets_response_status = open_tickets_response['status']

        if open_tickets_response_status not in range(200, 300):
            await self._notify_http_error_when_requesting_open_tickets_from_bruin_api(client_id, open_tickets_response)
            raise Exception

        open_tickets_ids = (ticket['ticketID'] for ticket in open_tickets_response_body)

        for ticket_id in open_tickets_ids:
            try:
                ticket_details_response = await self._get_ticket_details_by_ticket_id(ticket_id)
            except Exception:
                await self._notify_failing_rpc_request_for_ticket_details(ticket_id)
                continue

            ticket_details_response_body = ticket_details_response['body']
            ticket_details_response_status = ticket_details_response['status']

            if ticket_details_response_status not in range(200, 300):
                await self._notify_http_error_when_requesting_ticket_details_from_bruin_api(
                    client_id, ticket_id, ticket_details_response
                )
                continue

            ticket_details_list = ticket_details_response_body['ticketDetails']
            if not ticket_details_list:
                self._logger.info(f"Ticket {ticket_id} doesn't have any detail under ticketDetails key. Skipping...")
                continue

            result.append({
                'ticket_id': ticket_id,
                'ticket_detail': ticket_details_list[0],
                'ticket_notes': ticket_details_response_body['ticketNotes'],
            })

        return result

    async def _get_open_tickets_by_client_id(self, client_id):
        open_tickets_request = {
            'request_id': uuid(),
            'body': {
                'client_id': client_id,
                'ticket_status': ['New', 'InProgress', 'Draft'],
                'category': 'SD-WAN',
                'ticket_topic': 'VOO',
            },
        }

        open_tickets = await self._event_bus.rpc_request("bruin.ticket.request", open_tickets_request, timeout=90)
        return open_tickets

    async def _get_ticket_details_by_ticket_id(self, ticket_id):
        ticket_details_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id
            },
        }

        ticket_details = await self._event_bus.rpc_request(
            "bruin.ticket.details.request", ticket_details_request, timeout=15
        )
        return ticket_details

    async def _notify_failing_rpc_request_for_open_tickets(self, client_id):
        err_msg = f'An error occurred when requesting open tickets from Bruin API for client {client_id}'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_open_tickets_from_bruin_api(self, client_id, open_tickets_response):
        open_tickets_response_body = open_tickets_response['body']
        open_tickets_response_status = open_tickets_response['status']

        err_msg = (
            f'Error while retrieving open tickets for Bruin client {client_id} in '
            f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
            f'Error {open_tickets_response_status} - {open_tickets_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_failing_rpc_request_for_ticket_details(self, ticket_id):
        err_msg = f'An error occurred when requesting ticket details from Bruin API for ticket {ticket_id}'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_ticket_details_from_bruin_api(
            self, client_id, ticket_id, ticket_details_response):
        ticket_details_response_body = ticket_details_response['body']
        ticket_details_response_status = ticket_details_response['status']

        err_msg = (
            f'Error while retrieving ticket details for Bruin client {client_id} and ticket {ticket_id} in '
            f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
            f'Error {ticket_details_response_status} - {ticket_details_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    def _filter_tickets_related_to_edges_under_monitoring(self, tickets, serials_under_monitoring):
        return [
            ticket
            for ticket in tickets
            if ticket['ticket_detail']['detailValue'] in serials_under_monitoring
        ]

    def _distinguish_tickets_with_and_without_triage(self, tickets) -> tuple:
        tickets_with_triage = []
        for ticket in tickets:
            for note in ticket['ticket_notes']:
                if self.__triage_note_regex.match(note['noteValue']):
                    tickets_with_triage.append(ticket)
                    break

        tickets_without_triage = [
            ticket
            for ticket in tickets
            if ticket not in tickets_with_triage
        ]

        return tickets_with_triage, tickets_without_triage

    async def _process_tickets_with_triage(self, tickets, edges_by_serial):
        self._discard_non_triage_notes(tickets)

        for ticket in tickets:
            newest_triage_note = self._get_most_recent_ticket_note(ticket)

            if self._was_ticket_note_appended_recently(newest_triage_note):
                self._logger.info(f'The last triage note was appended to ticket {ticket["ticket_id"]} not long ago so '
                                  'no new triage note will be appended for now')
                continue

            ticket_id = ticket['ticket_id']
            serial_number = ticket['ticket_detail']['detailValue']
            newest_triage_note_timestamp = newest_triage_note['createdDate']
            edge_data = edges_by_serial[serial_number]

            await self._append_new_triage_notes_based_on_recent_events(
                ticket_id, newest_triage_note_timestamp, edge_data
            )

    def _discard_non_triage_notes(self, tickets) -> NoReturn:
        for ticket in tickets:
            ticket_notes = ticket['ticket_notes']

            for index, note in enumerate(ticket['ticket_notes']):
                is_triage_note = bool(self.__triage_note_regex.match(note['noteValue']))
                if not is_triage_note:
                    del ticket_notes[index]

    def _get_most_recent_ticket_note(self, ticket):
        sorted_notes = sorted(ticket['ticket_notes'], key=lambda note: note['createdDate'])
        return sorted_notes[-1]

    def _was_ticket_note_appended_recently(self, ticket_note):
        current_datetime = datetime.now(utc)
        ticket_note_creation_datetime = parse(ticket_note['createdDate']).astimezone(utc)

        return (current_datetime - ticket_note_creation_datetime) <= timedelta(minutes=30)

    async def _append_new_triage_notes_based_on_recent_events(self, ticket_id, last_triage_timestamp: str, edge_data):
        working_environment = self._config.TRIAGE_CONFIG['environment']

        edge_full_id = edge_data['edge_id']
        edge_identifier = EdgeIdentifier(**edge_full_id)

        last_triage_datetime = parse(last_triage_timestamp).astimezone(utc)

        try:
            recent_events_response = await self._get_last_events_for_edge(edge_full_id, since=last_triage_datetime)
        except Exception:
            await self._notify_failing_rpc_request_for_edge_events(edge_full_id)
            return

        recent_events_response_body = recent_events_response['body']
        recent_events_response_status = recent_events_response['status']

        if recent_events_response_status not in range(200, 300):
            await self._notify_http_error_when_requesting_edge_events_from_velocloud(
                edge_full_id, recent_events_response
            )
            return

        if not recent_events_response_body:
            self._logger.info(
                f'No events were found for edge {edge_identifier} starting from {last_triage_timestamp}. '
                f'Not appending any new triage notes to ticket {ticket_id}.'
            )
            return

        recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

        notes_were_appended = False
        for chunk in self._get_events_chunked(recent_events_response_body):
            triage_note_contents = self._compose_triage_note(chunk)

            if working_environment == 'production':
                try:
                    append_note_response = await self._append_note_to_ticket(ticket_id, triage_note_contents)
                except Exception:
                    await self._notify_failing_rpc_request_for_appending_ticket_note(ticket_id, triage_note_contents)
                    continue

                append_note_response_status = append_note_response['status']
                if append_note_response_status not in range(200, 300):
                    await self._notify_http_error_when_appending_note_to_ticket(ticket_id, append_note_response)
            else:
                self._logger.info(f'Not going to append a new triage note to ticket {ticket_id} as current environment '
                                  f'is {working_environment.upper()}. Triage note: {triage_note_contents}')

            notes_were_appended = True

        if notes_were_appended:
            enterprise_name = edge_data['edge_status']['enterprise_name']
            client_id = self._extract_client_id(enterprise_name)
            await self._notify_triage_note_was_appended_to_ticket(ticket_id, client_id)

    async def _notify_http_error_when_appending_note_to_ticket(self, ticket_id, append_note_response):
        append_note_response_body = append_note_response['body']
        append_note_response_status = append_note_response['status']

        err_msg = (
            f'Error while appending note to ticket {ticket_id} in {self._config.TRIAGE_CONFIG["environment"].upper()} '
            f'environment: Error {append_note_response_status} - {append_note_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _get_last_events_for_edge(self, edge_full_id, since: datetime):
        current_datetime = datetime.now(utc)

        last_events_request = {
            'request_id': uuid(),
            'body': {
                'edge': edge_full_id,
                'start_date': since,
                'end_date': current_datetime,
                'filter': ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD'],
            },
        }
        events = await self._event_bus.rpc_request(
            "alert.request.event.edge", last_events_request, timeout=180
        )
        return events

    async def _notify_failing_rpc_request_for_edge_events(self, edge_full_id):
        edge_identifier = EdgeIdentifier(**edge_full_id)
        err_msg = f'An error occurred when requesting edge events from Velocloud for edge {edge_identifier}'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_http_error_when_requesting_edge_events_from_velocloud(self, edge_full_id, edge_events_response):
        edge_identifier = EdgeIdentifier(**edge_full_id)

        edge_events_response_body = edge_events_response['body']
        edge_events_response_status = edge_events_response['status']

        err_msg = (
            f'Error while retrieving edge events for edge {edge_identifier} in '
            f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment: '
            f'Error {edge_events_response_status} - {edge_events_response_body}'
        )

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    def _get_events_chunked(self, events):
        events_per_chunk: int = self._config.TRIAGE_CONFIG['event_limit']
        number_of_events = len(events)
        chunks = (
            events[index:index + events_per_chunk]
            for index in range(0, number_of_events, events_per_chunk)
        )

        for chunk in chunks:
            yield chunk

    def _compose_triage_note(self, events):
        tz_object = timezone(self._config.TRIAGE_CONFIG["timezone"])

        triage_note_fragments = [
            '#*Automation Engine*#',
            'Triage',
        ]

        for event in events:
            event_type = event['event']
            event_category = event['category']
            event_message = event['message']
            event_time = event['eventTime']

            fragment_lines = [
                f'New event: {event_type}',
            ]

            if event_category == 'EDGE':
                fragment_lines.append('Device: Edge')
            else:
                iface_name_match = self.__event_interface_name_regex.match(event_message)
                interface_name = iface_name_match.group('interface_name') or iface_name_match.group('interface_name2')
                fragment_lines.append(f'Device: Interface {interface_name}')

            event_time_timezone_aware = parse(event_time).astimezone(tz_object)
            fragment_lines.append(f'Event time: {event_time_timezone_aware}')

            fragment = os.linesep.join(fragment_lines)
            triage_note_fragments.append(fragment)

        last_event_datetime = parse(events[len(events) - 1]["eventTime"]).astimezone(tz_object)
        triage_note_fragments.append(f'Timestamp: {last_event_datetime}')

        return f'{os.linesep * 2}'.join(triage_note_fragments)

    async def _append_note_to_ticket(self, ticket_id, ticket_note):
        append_note_to_ticket_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        append_ticket_to_note = await self._event_bus.rpc_request(
            "bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15
        )
        return append_ticket_to_note

    async def _notify_failing_rpc_request_for_appending_ticket_note(self, ticket_id, ticket_note):
        err_msg = f'An error occurred when appending a ticket note to ticket {ticket_id}. Ticket note: {ticket_note}'

        self._logger.error(err_msg)
        slack_message = {'request_id': uuid(), 'message': err_msg}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _notify_triage_note_was_appended_to_ticket(self, ticket_id, bruin_client_id):
        message = (f'Triage appended to ticket {ticket_id} in '
                   f'{self._config.TRIAGE_CONFIG["environment"].upper()} environment. Details at '
                   f'https://app.bruin.com/helpdesk?clientId={bruin_client_id}&ticketId={ticket_id}')

        self._logger.info(message)
        slack_message = {'request_id': uuid(), 'message': message}
        await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

    async def _process_tickets_without_triage(self, tickets, edges_by_serial):
        for ticket in tickets:
            ticket_id = ticket['ticket_id']

            serial_number = ticket['ticket_detail']['detailValue']
            edge_data = edges_by_serial[serial_number]
            edge_full_id = edge_data['edge_id']
            edge_identifier = EdgeIdentifier(**edge_full_id)

            past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)

            try:
                recent_events_response = await self._get_last_events_for_edge(
                    edge_full_id, since=past_moment_for_events_lookup
                )
            except Exception:
                await self._notify_failing_rpc_request_for_edge_events(edge_full_id)
                continue

            recent_events_response_body = recent_events_response['body']
            recent_events_response_status = recent_events_response['status']

            if recent_events_response_status not in range(200, 300):
                await self._notify_http_error_when_requesting_edge_events_from_velocloud(
                    edge_full_id, recent_events_response
                )
                return

            if not recent_events_response_body:
                self._logger.info(
                    f'No events were found for edge {edge_identifier} starting from {past_moment_for_events_lookup}. '
                    f'Not appending the first triage note to ticket {ticket_id}.'
                )
                return

            recent_events_response_body.sort(key=lambda event: event['eventTime'], reverse=True)

            relevant_info_for_triage_note = self._gather_relevant_data_for_first_triage_note(
                edge_data, recent_events_response_body
            )

            if self._config.TRIAGE_CONFIG['environment'] == 'dev':
                email_data = self._template_renderer.compose_email_object(relevant_info_for_triage_note)

                try:
                    await self._send_email(email_data)
                except Exception:
                    self._logger.error(f'An error occurred when sending email with data {email_data}')
            elif self._config.TRIAGE_CONFIG['environment'] == 'production':
                ticket_note = self._transform_relevant_data_into_ticket_note(relevant_info_for_triage_note)

                try:
                    append_note_response = await self._append_note_to_ticket(ticket_id, ticket_note)
                except Exception:
                    await self._notify_failing_rpc_request_for_appending_ticket_note(ticket_id, ticket_note)
                    continue

                append_note_response_status = append_note_response['status']
                if append_note_response_status not in range(200, 300):
                    await self._notify_http_error_when_appending_note_to_ticket(ticket_id, append_note_response)

    def _gather_relevant_data_for_first_triage_note(self, edge_data, edge_events) -> dict:
        edge_full_id = edge_data['edge_id']
        edge_status = edge_data['edge_status']

        host = edge_full_id['host']
        enterprise_id = edge_full_id['enterprise_id']
        edge_id = edge_full_id['edge_id']

        edge_status_data = edge_status['edges']
        edge_name = edge_status_data['name']
        edge_state = edge_status_data['edgeState']
        edge_serial = edge_status_data['serialNumber']

        edge_links = edge_status['links']

        velocloud_base_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor'
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_id}'

        relevant_data: dict = OrderedDict()

        relevant_data["Orchestrator Instance"] = host
        relevant_data["Edge Name"] = edge_name
        relevant_data["Links"] = {
            'Edge': f'{velocloud_edge_base_url}/',
            'QoE': f'{velocloud_edge_base_url}/qoe/',
            'Transport': f'{velocloud_edge_base_url}/links/',
            'Events': f'{velocloud_base_url}/events/',
        }

        relevant_data["Edge Status"] = edge_state
        relevant_data["Serial"] = edge_serial

        links_interface_names = []
        for link in edge_links:
            link_data = link['link']
            if not link_data:
                continue

            interface_name = link_data['interface']
            link_state = link_data['state']
            link_label = link_data['displayName']

            relevant_data[f'Interface {interface_name}'] = empty_str
            relevant_data[f'Interface {interface_name} Label'] = link_label
            relevant_data[f'Interface {interface_name} Status'] = link_state

            links_interface_names.append(interface_name)

        tz_object = timezone(self._config.TRIAGE_CONFIG['timezone'])

        relevant_data["Last Edge Online"] = None
        relevant_data["Last Edge Offline"] = None

        last_online_event_for_edge = self._get_first_element_matching(
            iterable=edge_events, condition=lambda event: event['event'] == 'EDGE_UP'
        )
        last_offline_event_for_edge = self._get_first_element_matching(
            iterable=edge_events, condition=lambda event: event['event'] == 'EDGE_DOWN'
        )

        if last_online_event_for_edge is not None:
            relevant_data["Last Edge Online"] = parse(last_online_event_for_edge['eventTime']).astimezone(tz_object)

        if last_offline_event_for_edge is not None:
            relevant_data["Last Edge Offline"] = parse(last_offline_event_for_edge['eventTime']).astimezone(tz_object)

        for interface_name in links_interface_names:
            last_online_key = f'Last {interface_name} Interface Online'
            last_offline_key = f'Last {interface_name} Interface Offline'

            relevant_data[last_online_key] = None
            relevant_data[last_offline_key] = None

            last_online_event_for_current_link = self._get_first_element_matching(
                iterable=edge_events,
                condition=lambda event: event['event'] == 'LINK_ALIVE' and self.__event_message_contains_interface_name(
                    event['message'], interface_name)
            )

            last_offline_event_for_current_link = self._get_first_element_matching(
                iterable=edge_events,
                condition=lambda event: event['event'] == 'LINK_DEAD' and self.__event_message_contains_interface_name(
                    event['message'], interface_name)
            )

            if last_online_event_for_current_link is not None:
                relevant_data[last_online_key] = parse(last_online_event_for_current_link['eventTime']).astimezone(
                    tz_object)

            if last_offline_event_for_current_link is not None:
                relevant_data[last_offline_key] = parse(last_offline_event_for_current_link['eventTime']).astimezone(
                    tz_object)

        return relevant_data

    def __event_message_contains_interface_name(self, event_message, interface_name):
        match = self.__event_interface_name_regex.match(event_message)

        interface_name_found = match.group('interface_name') or match.group('interface_name2')
        return interface_name == interface_name_found

    async def _send_email(self, email_message):
        return await self._event_bus.rpc_request("notification.email.request", email_message, timeout=10)

    def _transform_relevant_data_into_ticket_note(self, relevant_data: dict) -> str:
        ticket_note_lines = [
            '#*Automation Engine*#',
            'Triage',
        ]

        for key, value in relevant_data.items():
            if value is empty_str:
                ticket_note_lines.append(key)
            elif key == 'Links':
                clickable_links = [f'[{name}|{url}]' for name, url in value.items()]
                ticket_note_lines.append(f"Links: {' - '.join(clickable_links)}")
            else:
                ticket_note_lines.append(f'{key}: {value}')

        return os.linesep.join(ticket_note_lines)

    def _extract_client_id(self, enterprise_name):
        client_id_match = self.__client_id_regex.match(enterprise_name)

        if client_id_match:
            client_id = client_id_match.group('client_id')
            return int(client_id)
        else:
            return 9994

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback
