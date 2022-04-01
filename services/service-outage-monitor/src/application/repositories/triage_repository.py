import os
import re

from datetime import datetime
from typing import List

from dateutil.parser import parse
from pytz import timezone

from application import Outages


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

    def build_triage_note(self, cached_edge: dict, edge_status: dict, edge_events: List[dict],
                          outage_type: Outages, *, is_reopen_note=False) -> str:
        tz_object = timezone(self._config.TIMEZONE)

        edge_full_id = cached_edge['edge']
        host = edge_full_id['host']
        enterprise_id = edge_full_id['enterprise_id']
        edge_id = edge_full_id['edge_id']

        edge_name = edge_status['edgeName']
        edge_state = edge_status['edgeState']
        edge_serial = edge_status['edgeSerialNumber']
        edge_is_ha_primary = edge_status['edgeIsHAPrimary']

        is_outage_happening = outage_type is not None
        is_ha_outage = is_outage_happening and outage_type.name.startswith('HA_')
        ha_partner_serial = edge_status['edgeHASerialNumber']
        ha_partner_state = edge_status['edgeHAState']
        ha_partner_is_primary = not edge_is_ha_primary

        edge_links = edge_status['links']
        links_configuration = cached_edge.get('links_configuration', [])

        velocloud_base_url = f'https://{host}/#!/operator/customer/{enterprise_id}/monitor'
        velocloud_edge_base_url = f'{velocloud_base_url}/edge/{edge_id}'

        ticket_note_lines = [
            "#*MetTel's IPA*#",
        ]

        if is_reopen_note:
            ticket_note_lines += [
                'Re-opening ticket.',
                '',
            ]
        else:
            ticket_note_lines += [
                'Triage (VeloCloud)',
                '',
            ]

        if outage_type is Outages.HA_SOFT_DOWN:
            ticket_note_lines.append('High Availability - Edge Offline\n')
        elif outage_type is Outages.HA_HARD_DOWN:
            ticket_note_lines.append('High Availability - Location Offline\n')

        ticket_note_lines += [
            f'Orchestrator Instance: {host}',
            f'Edge Name: {edge_name}',
            (
                'Links: '
                f'[Edge|{velocloud_edge_base_url}/] - [QoE|{velocloud_edge_base_url}/qoe/] - '
                f'[Transport|{velocloud_edge_base_url}/links/] - [Events|{velocloud_base_url}/events/]'
            ),
            '',
        ]

        if outage_type is Outages.HA_HARD_DOWN:
            ticket_note_lines.append('Both primary and secondary edges are DISCONNECTED.\n')

        if not is_outage_happening or is_ha_outage:
            if edge_is_ha_primary:
                primary_serial = edge_serial
                primary_state = edge_state
            else:
                primary_serial = ha_partner_serial
                primary_state = ha_partner_state

            ticket_note_lines += [
                f'Serial: {primary_serial}',
                f'Edge Status: {primary_state}',
                'HA Role: Primary',
            ]
        else:
            ticket_note_lines += [
                f'Serial: {edge_serial}',
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

        if not is_outage_happening or is_ha_outage:
            if ha_partner_is_primary:
                standby_serial = edge_serial
                standby_state = edge_state
            else:
                standby_serial = ha_partner_serial
                standby_state = ha_partner_state

            ticket_note_lines += [
                f'Serial: {standby_serial}',
                f'Edge Status: {"STANDBY READY" if standby_state == "CONNECTED" else standby_state}',
                'HA Role: Standby',
            ]
            if standby_state == 'OFFLINE':
                ticket_note_lines.append(f'Timestamp: {datetime.now(tz_object)}')
            ticket_note_lines.append('')

        for link in edge_links:
            if not link:
                continue

            interface_name = link['interface']
            link_state = link['linkState']
            link_label = link['displayName']
            link_ip = link['linkIpAddress']
            link_interface_type = "Unknown"
            for link_configuration in links_configuration:
                if interface_name in link_configuration['interfaces']:
                    link_interface_type = (
                        f"{link_configuration['mode'].capitalize()} {link_configuration['type'].capitalize()}"
                    )
                    break

            ticket_note_lines.append(f'Interface {interface_name}')
            ticket_note_lines.append(f'Interface {interface_name} Label: {link_label}')
            ticket_note_lines.append(f'Interface {interface_name} IP Address: {link_ip}')
            ticket_note_lines.append(f'Interface {interface_name} Type: {link_interface_type}')
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
        tz_object = timezone(self._config.TIMEZONE)

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
