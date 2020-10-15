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

        last_online_event_for_edge = self._utils_repository.get_first_element_matching(
            iterable=edge_events, condition=lambda event: event['event'] == 'EDGE_UP'
        )
        last_offline_event_for_edge = self._utils_repository.get_first_element_matching(
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
                relevant_data[last_online_key] = parse(last_online_event_for_current_link['eventTime']).astimezone(
                    tz_object)

            if last_offline_event_for_current_link is not None:
                relevant_data[last_offline_key] = parse(last_offline_event_for_current_link['eventTime']).astimezone(
                    tz_object)

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

    def build_events_note(self, events):
        tz_object = timezone(self._config.TRIAGE_CONFIG["timezone"])

        triage_note_fragments = [
            '#*Automation Engine*#',
            'Triage',
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
