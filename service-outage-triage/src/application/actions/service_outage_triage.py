import base64

import json
import re
from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil.parser import parse
from apscheduler.util import undefined
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class ServiceOutageTriage:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer

    async def start_service_outage_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every '
                          f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._poll_tickets, 'interval', minutes=self._config.TRIAGE_CONFIG["polling_minutes"],
                                next_run_time=next_run_time,
                                replace_existing=True, id='_service_outage_triage_process')

    async def _poll_tickets(self):
        self._logger.info("Requesting tickets from Bruin")
        ticket_request_msg_titan = {'request_id': uuid(), 'client_id': 85940,
                                    'ticket_status': ['New', 'InProgress', 'Draft'],
                                    'category': 'SD-WAN',
                                    'ticket_topic': 'VOO'}
        ticket_request_msg_mettel = {'request_id': uuid(), 'client_id': 9994,
                                     'ticket_status': ['New', 'InProgress', 'Draft'],
                                     'category': 'SD-WAN',
                                     'ticket_topic': 'VOO'}
        all_tickets_titan = await self._event_bus.rpc_request("bruin.ticket.request",
                                                              json.dumps(ticket_request_msg_titan, default=str),
                                                              timeout=90)
        all_tickets_mettel = await self._event_bus.rpc_request("bruin.ticket.request",
                                                               json.dumps(ticket_request_msg_mettel, default=str),
                                                               timeout=90)
        all_tickets = all_tickets_titan
        all_tickets["tickets"] = all_tickets["tickets"] + all_tickets_mettel["tickets"]

        filtered_ticket_ids = []
        if all_tickets is not None and "tickets" in all_tickets.keys() and all_tickets["tickets"] is not None:
            filtered_ticket_ids = await self._filtered_ticket_details(all_tickets)
        else:
            self._logger.error(f'Tickets returned {json.dumps(all_tickets)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Service outage triage: Error in ticket list. '
                                        f'Ticket list: {json.dumps(all_tickets)}. '
                                        f'Environment: {self._config.TRIAGE_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        for ticket_id in filtered_ticket_ids:
            id_by_serial = self._config.TRIAGE_CONFIG["id_by_serial"]
            edge_id = id_by_serial[ticket_id["serial"]]
            status_msg = {'request_id': uuid(),
                          'edge': edge_id}

            filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
            events_msg = {'request_id': uuid(),
                          'edge': edge_id,
                          'start_date': (datetime.now(utc) - timedelta(days=7)),
                          'end_date': datetime.now(utc),
                          'filter': filter_events_status_list}

            edge_status = await self._event_bus.rpc_request("edge.status.request",
                                                            json.dumps(status_msg, default=str), timeout=10)
            client_id = self._client_id_from_edge_status(edge_status)
            edge_events = await self._event_bus.rpc_request("alert.request.event.edge",
                                                            json.dumps(events_msg, default=str), timeout=180)
            ticket_dict = self._compose_ticket_note_object(edge_status, edge_events)
            if self._config.TRIAGE_CONFIG['environment'] == 'production':
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_append_note_msg = {'request_id': uuid(),
                                          'ticket_id': ticket_id["ticketID"],
                                          'note': ticket_note}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  json.dumps(ticket_append_note_msg),
                                                  timeout=15)
            elif self._config.TRIAGE_CONFIG['environment'] == 'dev':
                ticket_note = self._template_renderer._ticket_object_to_email_obj(ticket_dict)
                await self._event_bus.rpc_request("notification.email.request",
                                                  json.dumps(ticket_note),
                                                  timeout=10)
            slack_message = {'request_id': uuid(),
                             'message': f'Triage appended to ticket: '
                                        f'https://app.bruin.com/helpdesk?clientId={client_id}&ticketId='
                                        f'{ticket_id["ticketID"]}, in '
                                        f'{self._config.TRIAGE_CONFIG["environment"]}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        self._logger.info("End of ticket polling job")

    async def _filtered_ticket_details(self, ticket_list):
        filtered_ticket_ids = []
        valid_serials = list(self._config.TRIAGE_CONFIG["id_by_serial"].keys())
        for ticket in ticket_list['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               json.dumps(ticket_detail_msg, default=str),
                                                               timeout=15)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                triage_exists = False
                if 'detailValue' in ticket_detail.keys():
                    if ticket_detail['detailValue'] in valid_serials:
                        ticket_item = dict()
                        ticket_item["ticketID"] = ticket['ticketID']
                        ticket_item["serial"] = ticket_detail['detailValue']
                        sorted_ticket_notes = sorted(ticket_details['ticket_details']['ticketNotes'],
                                                     key=lambda note: note['createdDate'], reverse=True)
                        for ticket_note in sorted_ticket_notes:
                            if ticket_note['noteValue'] is not None:
                                if '#*Automation Engine*#' in ticket_note['noteValue']:
                                    self._logger.info(f'Triage already exists for ticket id of {ticket["ticketID"]}')
                                    if 'TimeStamp: ' in ticket_note['noteValue']:
                                        last_timestamp = self._extract_field_from_string(ticket_note['noteValue'],
                                                                                         "TimeStamp: ")
                                        timestamp_difference = datetime.now(timezone('US/Eastern')
                                                                            ) - parse(last_timestamp)
                                        if timestamp_difference > timedelta(minutes=30):
                                            await self._check_for_new_events(last_timestamp, ticket_item)
                                    triage_exists = True
                                    break
                        if not triage_exists:
                            filtered_ticket_ids.append(ticket_item)
                        break
        return filtered_ticket_ids

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in event_list:
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        time = parse(event_obj['eventTime'])
                        return time.astimezone(timezone('US/Eastern'))
                else:
                    time = parse(event_obj['eventTime'])
                    return time.astimezone(timezone('US/Eastern'))
        return None

    def _extract_field_from_string(self, dict_as_string, key1, key2='#DEFAULT_END#'):
        return dict_as_string[dict_as_string.find(key1) + len(key1): dict_as_string.find(key2)]

    def _client_id_from_edge_status(self, edge_status):
        client_id = edge_status['edge_info']['enterprise_name'].split('|')
        if len(client_id) < 2:
            # If after the split, the length of the array is lesser than 2 it means is a mettel edge
            # So we hardcode mettel's bruin client ID
            client_id = 9994
        return client_id

    async def _check_for_new_events(self, timestamp, ticket_id):
        id_by_serial = self._config.TRIAGE_CONFIG["id_by_serial"]
        edge_id = id_by_serial[ticket_id["serial"]]
        filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
        events_msg = {'request_id': uuid(),
                      'edge': edge_id,
                      'start_date': timestamp,
                      'end_date': datetime.now(timezone('US/Eastern')),
                      'filter': filter_events_status_list}
        edge_status_request = {
            'request_id': uuid(),
            'edge': edge_id,
        }
        edge_status = await self._event_bus.rpc_request(
            'edge.status.request',
            json.dumps(edge_status_request),
            timeout=45,
        )
        client_id = self._client_id_from_edge_status(edge_status)
        edge_events = await self._event_bus.rpc_request("alert.request.event.edge", json.dumps(
            events_msg, default=str), timeout=180)

        event_list = edge_events['events']

        if len(event_list) > 0:
            sorted_event_list = sorted(event_list, key=lambda event: event['eventTime'])

            event_str = self._compose_event_note_object(sorted_event_list)

            quotient = len(event_str) // 1000
            step_amount = len(sorted_event_list)

            if quotient == 2 or quotient == 1:
                step_amount = (len(sorted_event_list)) // 2
            if quotient > 2:
                if len(event_str) % 1000 == 0:
                    split_amount = quotient - 1
                else:
                    split_amount = quotient
                step_amount = (len(sorted_event_list) // split_amount)

            split_event_lists = [sorted_event_list[i:i + step_amount] for i in range(0, len(sorted_event_list),
                                                                                     step_amount)]
            for events in split_event_lists:
                event_obj = self._compose_event_note_object(events)
                event_timestamp = parse(events[len(events) - 1]["eventTime"]).astimezone(timezone("US/Eastern"))
                event_ticket_note = "#*Automation Engine*#" + event_obj + 'TimeStamp: ' + str(
                    event_timestamp + timedelta(seconds=1))
                if self._config.TRIAGE_CONFIG['environment'] == 'production':
                    ticket_append_note_msg = {'request_id': uuid(),
                                              'ticket_id': ticket_id["ticketID"],
                                              'note': event_ticket_note}
                    await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                      json.dumps(ticket_append_note_msg),
                                                      timeout=15)
                    slack_message = {'request_id': uuid(),
                                     'message': f'Events appended to ticket: '
                                                f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                                f'ticketId={ticket_id["ticketID"]}, in '
                                                f'{self._config.TRIAGE_CONFIG["environment"]}'}
                    await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message),
                                                      timeout=10)
                self._logger.info(event_ticket_note)

    def _compose_event_note_object(self, event_list):
        full_event_str = ""
        for event in event_list:
            event_str = f'NewEvent: {event["event"]}\n'
            if event['category'] == 'EDGE':
                event_str = event_str + 'Device: Edge\n'
            else:
                if 'GE1' in event['message']:
                    event_str = event_str + f'Device: Interface GE1\n'
                if 'GE2' in event['message']:
                    event_str = event_str + f'Device: Interface GE2\n'
            event_str = event_str + f'eventTime: {parse(event["eventTime"]).astimezone(timezone("US/Eastern"))}\n'
            full_event_str = full_event_str + '\n' + event_str
        return full_event_str

    def _compose_ticket_note_object(self, edges_status_to_report, edges_events_to_report):

        edge_triage_dict = OrderedDict()

        edge_triage_dict["Orchestrator instance"] = edges_status_to_report['edge_id']['host']
        edge_triage_dict["Edge Name"] = edges_status_to_report["edge_info"]["edges"]["name"]
        edge_triage_dict["Links"] = \
            f'[Edge|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/] - ' \
            f'[QoE|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/qoe/] - ' \
            f'[Transport|https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/] - ' \
            f'[Events|https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
            f'operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/events/] \n'

        edge_triage_dict["Edge Status"] = edges_status_to_report["edge_info"]["edges"]["edgeState"]

        edge_triage_dict["Interface LABELMARK1"] = None
        edge_triage_dict["Label LABELMARK2"] = None
        edge_triage_dict["Interface GE1 Status"] = "Interface GE1 not available"

        edge_triage_dict["Interface LABELMARK3"] = None
        edge_triage_dict["Label LABELMARK4"] = None
        edge_triage_dict["Interface GE2 Status"] = "Interface GE2 not available\n"

        link_data = dict()

        link_data["GE1"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE1"]
        link_data["GE2"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE2"]
        # Check if linkdata return an empty list due to None links
        if len(link_data["GE1"]) > 0:
            edge_triage_dict["Interface LABELMARK1"] = link_data["GE1"][0]["link"]["interface"]
            edge_triage_dict["Interface GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_triage_dict["Label LABELMARK2"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_triage_dict["Interface LABELMARK3"] = link_data["GE2"][0]["link"]["interface"]
            edge_triage_dict["Interface GE2 Status"] = f'{link_data["GE2"][0]["link"]["state"]}\n'
            edge_triage_dict["Label LABELMARK4"] = link_data["GE2"][0]["link"]['displayName']

        edge_triage_dict["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"],
                                                                                    'EDGE_UP')
        edge_triage_dict["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"],
                                                                                     'EDGE_DOWN')
        edge_triage_dict["Last GE1 Interface Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                             ["events"],
                                                                                             'LINK_ALIVE',
                                                                                             'Link GE1 is no'
                                                                                             ' longer DEAD')
        edge_triage_dict["Last GE1 Interface Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                              ["events"],
                                                                                              'LINK_DEAD',
                                                                                              'Link GE1 is now DEAD')
        edge_triage_dict["Last GE2 Interface Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                             ["events"],
                                                                                             'LINK_ALIVE',
                                                                                             'Link GE2 is no'
                                                                                             ' longer DEAD')
        edge_triage_dict["Last GE2 Interface Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                              ["events"],
                                                                                              'LINK_DEAD',
                                                                                              'Link GE2 is now DEAD')
        edge_triage_dict["TimeStamp"] = datetime.now(timezone('US/Eastern'))
        return edge_triage_dict

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
