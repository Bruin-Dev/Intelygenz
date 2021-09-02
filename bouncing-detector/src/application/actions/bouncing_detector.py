import re
import time
from collections import OrderedDict
from collections import defaultdict
from datetime import datetime
from typing import Callable

from apscheduler.util import undefined
from pytz import timezone


class BouncingDetector:

    def __init__(self, event_bus, logger, scheduler, config, bruin_repository, velocloud_repository,
                 customer_cache_repository, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._customer_cache_repository = customer_cache_repository
        self._notifications_repository = notifications_repository

    async def start_bouncing_detector_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: Bouncing Detector')
        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.BOUNCING_DETECTOR_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')

        self._scheduler.add_job(self._bouncing_detector_process, 'interval',
                                minutes=self._config.BOUNCING_DETECTOR_CONFIG["monitoring_minutes_interval"],
                                next_run_time=next_run_time,
                                replace_existing=True,
                                id='_bouncing_detector')

    async def _bouncing_detector_process(self):
        self._logger.info(f"Starting bouncing detector process to find any circuit instability "
                          f"in host {self._config.BOUNCING_DETECTOR_CONFIG['velocloud_host']} ")
        start = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        if customer_cache_response['status'] not in range(200, 300) or customer_cache_response['status'] == 202:
            return

        self._customer_cache: list = customer_cache_response['body']
        if not self._customer_cache:
            self._logger.info('Got an empty customer cache. Skipping process...')
            return

        link_metrics_response = await self._velocloud_repository.get_last_link_metrics()
        if link_metrics_response['status'] not in range(200, 300):
            return
        self._link_metrics_response = link_metrics_response["body"]

        enterprise_to_edge_info = self._get_enterprise_to_cached_info_dict()
        events_by_serial = await self._get_events_by_serial_dict(enterprise_to_edge_info)
        await self._check_for_bouncing_events(events_by_serial)
        stop = time.time()
        self._logger.info(f'Bouncing detector process finished! Elapsed time:'
                          f'{round((stop - start) / 60, 2)} minutes')

    def _get_enterprise_to_cached_info_dict(self):
        self._logger.info('Organizing customer cache by enterprise_id')
        enterprise_to_edge_info = defaultdict(list)
        for edge_info in self._customer_cache:
            enterprise_to_edge_info[edge_info['edge']['enterprise_id']].append(edge_info)
        return enterprise_to_edge_info

    async def _get_events_by_serial_dict(self, enterprise_to_edge_info):
        events_by_serial = defaultdict(list)
        self._logger.info('Creating events by serial dict')
        for enterprise_id in enterprise_to_edge_info:
            enterprise_events_response = await self._velocloud_repository.get_last_enterprise_events(enterprise_id)
            if enterprise_events_response['status'] not in range(200, 300):
                return events_by_serial
            enterprise_events = enterprise_events_response['body']
            for event in enterprise_events:
                cached_edge_info = self._get_first_element_matching(
                    enterprise_to_edge_info[enterprise_id],
                    lambda edge: edge["edge_name"] == event["edgeName"],
                )
                if cached_edge_info is None:
                    self._logger.info(f'No edge in the customer cache had edge name {event["edgeName"]}. Skipping...')
                    continue
                serial = cached_edge_info["serial_number"]
                self._logger.info(f'Event with edge name {event["edgeName"]} matches edge from customer cache with'
                                  f'serial number {serial}. Appending event to serial {serial} '
                                  f'in event_by_serial dict ')

                events_by_serial[serial].append(event)
        return events_by_serial

    async def _check_for_bouncing_events(self, events_by_serial):
        for serial in events_by_serial:
            self._logger.info(f'Checking serial {serial} for circuit instability')
            await self._check_for_bouncing_edge_events(serial, events_by_serial[serial])
            await self._check_for_bouncing_link_events(serial, events_by_serial[serial])

    async def _check_for_bouncing_edge_events(self, serial, event_list):
        edge_down_events = [event for event in event_list if event['event'] == 'EDGE_DOWN']
        if len(edge_down_events) >= self._config.BOUNCING_DETECTOR_CONFIG['event_threshold']:
            self._logger.info(f'Circuit Instability detected in edge with serial {serial}. {len(edge_down_events)}'
                              f'EDGE_DOWN events were detected.')
            cached_edge_info = self._get_first_element_matching(
                self._customer_cache,
                lambda edge: edge["serial_number"] == serial,
            )
            ticket_dict = self._get_edge_ticket_dict(cached_edge_info, len(edge_down_events))
            await self._create_bouncing_ticket(cached_edge_info, ticket_dict, serial)

    async def _check_for_bouncing_link_events(self, serial, event_list):
        link_down_events = defaultdict(list)
        for event in event_list:
            if event['event'] != 'LINK_DEAD':
                continue
            interface = event['message'].split()[1]
            link_down_events[interface].append(event)
        for interface in link_down_events:
            if len(link_down_events[interface]) >= self._config.BOUNCING_DETECTOR_CONFIG['event_threshold']:
                cached_edge_info = self._get_first_element_matching(
                    self._customer_cache,
                    lambda edge: edge["serial_number"] == serial,
                )
                link_info = self._get_first_element_matching(
                    self._link_metrics_response,
                    lambda link: (link["link"]["edgeSerialNumber"] == serial and link[
                        "link"]["interface"] == interface),
                )
                if link_info is None:
                    self._logger.info(f'No link info is available for interface {interface} in serial {serial}')
                    continue

                self._logger.info(f'Circuit Instability detected in edge with serial {serial} for interface link: '
                                  f'{interface}. {len(link_down_events[interface])} LINK_DEAD events were detected.')

                ticket_dict = self._get_link_ticket_dict(cached_edge_info, link_info["link"], interface,
                                                         len(link_down_events[interface]))
                await self._create_bouncing_ticket(cached_edge_info, ticket_dict, serial)

    def _get_edge_ticket_dict(self, edge_info, length_of_events):

        edge_overview = OrderedDict()
        edge_overview["Edge Name"] = edge_info['edge_name']
        edge_overview['Interval for Scan'] = self._config.BOUNCING_DETECTOR_CONFIG['monitoring_minutes_interval']
        edge_overview["Threshold"] = self._config.BOUNCING_DETECTOR_CONFIG['event_threshold']
        edge_overview["Events"] = length_of_events

        edge_overview['Scan Time'] = datetime.now(timezone(self._config.BOUNCING_DETECTOR_CONFIG['timezone']))

        edge_overview["Links"] = \
            f'[Edge|https://{edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{edge_info["edge"]["edge_id"]}/] - ' \
            f'[QoE|https://{edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{edge_info["edge"]["edge_id"]}/qoe/] - ' \
            f'[Transport|https://{edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{edge_info["edge"]["edge_id"]}/links/] \n'
        return edge_overview

    def _get_link_ticket_dict(self, cached_edge_info, link_info, interface, length_of_events):
        links_configuration = cached_edge_info.get('links_configuration', [])

        edge_overview = OrderedDict()
        edge_overview["Edge Name"] = link_info['edgeName']
        edge_overview["Name"] = link_info['displayName']
        edge_overview["Interface"] = interface
        link_interface_type = "Unknown"
        for link_configuration in links_configuration:
            if interface in link_configuration['interfaces']:
                link_interface_type = (
                    f"{link_configuration['mode'].capitalize()} {link_configuration['type'].capitalize()}"
                )
                break
        edge_overview["Link Type"] = link_interface_type
        edge_overview['Interval for Scan'] = self._config.BOUNCING_DETECTOR_CONFIG['monitoring_minutes_interval']
        edge_overview["Threshold"] = self._config.BOUNCING_DETECTOR_CONFIG['event_threshold']
        edge_overview["Events"] = length_of_events

        edge_overview['Scan Time'] = datetime.now(timezone(self._config.BOUNCING_DETECTOR_CONFIG['timezone']))

        edge_overview["Links"] = \
            f'[Edge|https://{cached_edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{cached_edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{cached_edge_info["edge"]["edge_id"]}/] - ' \
            f'[QoE|https://{cached_edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{cached_edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{cached_edge_info["edge"]["edge_id"]}/qoe/] - ' \
            f'[Transport|https://{cached_edge_info["edge"]["host"]}/#!/operator/customer/' \
            f'{cached_edge_info["edge"]["enterprise_id"]}' \
            f'/monitor/edge/{cached_edge_info["edge"]["edge_id"]}/links/] \n'
        return edge_overview

    async def _create_bouncing_ticket(self, edge_cached_info, ticket_dict, serial):
        self._logger.info(f'Attempting service affecting ticket creation for edge with serial {serial}')

        ticket_note = self._ticket_object_to_string(ticket_dict)

        if self._config.BOUNCING_DETECTOR_CONFIG['environment'] == 'production':
            client_id = edge_cached_info['bruin_client_info']['client_id']

            ticket = await self._bruin_repository.get_affecting_ticket(client_id, serial)
            if ticket is None:
                return
            if len(ticket) == 0:
                contact_info = self._get_contact_info(serial)
                if contact_info is None:
                    self._logger.info(f'No contact info found for serial {serial}. Skipping ticket creation ..')
                    return
                response = await self._bruin_repository.create_affecting_ticket(client_id, serial,
                                                                                contact_info["contacts"])
                if response["status"] not in range(200, 300):
                    return
                ticket_id = response["body"]["ticketIds"][0]

                await self._bruin_repository.append_note_to_ticket(ticket_id=ticket_id,
                                                                   note=ticket_note)

                slack_message = f'Circuit Instability Ticket created with ticket id: {ticket_id}\n' \
                                f'https://app.bruin.com/helpdesk?clientId={client_id}&' \
                                f'ticketId={ticket_id} , in ' \
                                f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"]}'
                await self._notifications_repository.send_slack_message(slack_message)

                self._logger.info(f'Ticket created with ticket id: {ticket_id}')

                return
            else:
                ticket_details = self._bruin_repository.find_detail_by_serial(ticket, serial)
                if not ticket_details:
                    self._logger.error(f"No ticket details matching the serial number {serial}")
                    return
                if self._is_ticket_resolved(ticket_details):
                    self._logger.info(f'A resolved service Affecting ticket '
                                      f'detected in edge with serial {serial}. '
                                      f'Ticket: {ticket}. Re-opening ticket..')
                    ticket_id = ticket['ticketID']
                    detail_id = ticket_details['detailID']
                    open_ticket_response = await self._bruin_repository.open_ticket(ticket_id, detail_id)
                    if open_ticket_response['status'] not in range(200, 300):
                        return
                    slack_message = (
                        f'Affecting ticket {ticket_id} reopened through bouncing-detector service. '
                        f'Details at https://app.bruin.com/t/{ticket_id}'
                    )
                    reopen_ticket_note = self._ticket_object_to_string_without_watermark(ticket_dict)

                    await self._notifications_repository.send_slack_message(slack_message)
                    await self._bruin_repository.append_reopening_note_to_ticket(ticket_id, reopen_ticket_note)

                else:
                    self._logger.info(f'A unresolved service Affecting ticket '
                                      f'detected in edge with serial {serial}. '
                                      f'Ticket: {ticket}. Appending ticket note..')
                    ticket_id = ticket["ticketID"]
                    await self._bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

                    slack_message = f'Appending Circuit Instability note to unresolved ticket ' \
                                    f'with ticket id: {ticket_id}\n' \
                                    f'https://app.bruin.com/t/{ticket_id} , in ' \
                                    f'{self._config.BOUNCING_DETECTOR_CONFIG["environment"]}'
                    await self._notifications_repository.send_slack_message(slack_message)

    def _ticket_object_to_string(self, ticket_dict, watermark=None):
        edge_triage_str = "#*MetTel's IPA*#\n"
        if watermark is not None:
            edge_triage_str = f"{watermark}\n"
        edge_triage_str = edge_triage_str + 'Trouble: Circuit Instability\n\n'
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]}\n'
        return edge_triage_str

    def _ticket_object_to_string_without_watermark(self, ticket_dict):
        return self._ticket_object_to_string(ticket_dict, "")

    def _get_contact_info(self, serial):
        contact_info = self._get_first_element_matching(
            self._config.BOUNCING_DETECTOR_CONFIG['device_by_id'],
            lambda edge: edge["serial"] == serial,
        )
        return contact_info

    def _is_ticket_resolved(self, ticket_detail: dict) -> bool:
        return ticket_detail['detailStatus'] == 'R'

    @staticmethod
    def _get_first_element_matching(iterable, condition: Callable, fallback=None):
        try:
            return next(elem for elem in iterable if condition(elem))
        except StopIteration:
            return fallback
