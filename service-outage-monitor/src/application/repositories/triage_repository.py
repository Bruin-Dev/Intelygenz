import os
import re

from collections import OrderedDict
from typing import List

from dateutil.parser import parse
from pytz import timezone


empty_str = str()

EVENT_INTERFACE_NAME_REGEX = re.compile(
    r'(^Interface (?P<interface_name>[a-zA-Z0-9]+) is (up|down)$)|'
    r'(^Link (?P<interface_name2>[a-zA-Z0-9]+) is (no longer|now) DEAD$)'
)


class TriageRepository:
    def __init__(self, config, utils_repository):
        self._config = config
        self._utils_repository = utils_repository

    def __event_message_contains_interface_name(self, event_message, interface_name):
        match = EVENT_INTERFACE_NAME_REGEX.match(event_message)

        interface_name_found = match.group('interface_name') or match.group('interface_name2')
        return interface_name == interface_name_found

    def build_triage_note(self, edge_full_id: dict, edge_status: dict, edge_events: List[dict]) -> str:
        tz_object = timezone(self._config.TRIAGE_CONFIG['timezone'])

        host = edge_full_id['host']
        enterprise_id = edge_full_id['enterprise_id']
        edge_id = edge_full_id['edge_id']

        edge_name = edge_status['edgeName']
        edge_state = edge_status['edgeState']
        edge_serial = edge_status['edgeSerialNumber']

        edge_links = edge_status['links']

        velocloud_base_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor'
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_id}'

        ticket_note_lines = [
            "#*MetTel's IPA*#",
            'Triage (VeloCloud)',
            f'Orchestrator Instance: {host}',
            f'Edge Name: {edge_name}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
            f'Serial: {edge_serial}',
            '',
            f'Edge Status: {edge_state}',
        ]

        last_online_event_for_edge = self._utils_repository.get_first_element_matching(
            iterable=edge_events, condition=lambda event: event['event'] == 'EDGE_UP'
        )
        last_offline_event_for_edge = self._utils_repository.get_first_element_matching(
            iterable=edge_events, condition=lambda event: event['event'] == 'EDGE_DOWN'
        )

        if last_online_event_for_edge is not None:
            ticket_note_lines.append(
                f"Last Edge Online: {parse(last_online_event_for_edge['eventTime']).astimezone(tz_object)}"
            )
        else:
            ticket_note_lines.append("Last Edge Online: Unknown")

        if last_offline_event_for_edge is not None:
            ticket_note_lines.append(
                f"Last Edge Offline: {parse(last_offline_event_for_edge['eventTime']).astimezone(tz_object)}\n"
            )
        else:
            ticket_note_lines.append("Last Edge Offline: Unknown\n")

        for link in edge_links:
            if not link:
                continue

            interface_name = link['interface']
            link_state = link['linkState']
            link_label = link['displayName']

            ticket_note_lines.append(f'Interface {interface_name}')
            ticket_note_lines.append(f'Interface {interface_name} Label: {link_label}')
            ticket_note_lines.append(f'Interface {interface_name} Status: {link_state}')

            last_online_event_for_current_link = self._utils_repository.get_first_element_matching(
                iterable=edge_events,
                condition=lambda event: event['event'] == 'LINK_ALIVE' and self.__event_message_contains_interface_name(
                    event['message'], interface_name)
            )

            last_offline_event_for_current_link = self._utils_repository.get_first_element_matching(
                iterable=edge_events,
                condition=lambda event: event['event'] == 'LINK_DEAD' and self.__event_message_contains_interface_name(
                    event['message'], interface_name)
            )

            if last_online_event_for_current_link is not None:
                last_online_event_time = last_online_event_for_current_link['eventTime']
                ticket_note_lines.append(
                    f'Last {interface_name} Interface Online: {parse(last_online_event_time).astimezone(tz_object)}'
                )
            else:
                ticket_note_lines.append(f'Last {interface_name} Interface Online: Unknown')

            if last_offline_event_for_current_link is not None:
                last_offline_event_time = last_offline_event_for_current_link['eventTime']
                ticket_note_lines.append(
                    f'Last {interface_name} Interface Offline: {parse(last_offline_event_time).astimezone(tz_object)}\n'
                )
            else:
                ticket_note_lines.append(f'Last {interface_name} Interface Offline: Unknown\n')

        return os.linesep.join(ticket_note_lines).strip()

    def build_events_note(self, events):
        tz_object = timezone(self._config.TRIAGE_CONFIG["timezone"])

        triage_note_fragments = [
            "#*MetTel's IPA*#",
            'Triage (VeloCloud)',
            '',
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
                iface_name_match = EVENT_INTERFACE_NAME_REGEX.match(event_message)
                interface_name = iface_name_match.group('interface_name') or iface_name_match.group('interface_name2')
                fragment_lines.append(f'Device: Interface {interface_name}')

            event_time_timezone_aware = parse(event_time).astimezone(tz_object)
            fragment_lines.append(f'Event time: {event_time_timezone_aware}')
            fragment_lines.append('')

            fragment = os.linesep.join(fragment_lines)
            triage_note_fragments.append(fragment)

        last_event_datetime = parse(events[len(events) - 1]["eventTime"]).astimezone(tz_object)
        triage_note_fragments.append(f'Timestamp: {last_event_datetime}')

        return f'{os.linesep}'.join(triage_note_fragments)
