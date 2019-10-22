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

ODD_ROW = '<tr>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%KEY%%</td>' \
          '<td class="odd" bgcolor="#EDEFF0" style="background-color: #EDEFF0; color: #596872; font-weight: normal; ' \
          'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
          'white-space: nowrap">%%VALUE%%</td>' \
          ' </tr>'

EVEN_ROW = ' <tr>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%KEY%%</td>' \
           '<td class="even" bgcolor="#FFFFFF" style="background-color: #FFFFFF; ' \
           'color: #596872; font-weight: normal; ' \
           'font-size: 14px; line-height: 20px; padding: 15px; letter-spacing: 0.05em; border: 1px solid #DDDDDD; ' \
           'white-space: nowrap">%%VALUE%%</td>' \
           '</tr>'


class ServiceOutageTriage:

    def __init__(self, event_bus: EventBus, logger, scheduler, service_id, config):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._service_id = service_id
        self._config = config

    async def start_service_outage_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every minute')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._poll_tickets, 'interval', seconds=120, next_run_time=next_run_time,
                                replace_existing=True, id='_service_outage_triage_process')

    async def _poll_tickets(self):
        self._logger.info("Requesting tickets from Bruin")
        ticket_request_msg = {'request_id': uuid(), 'response_topic': f'bruin.ticket.response.{self._service_id}',
                              'client_id': 85940, 'ticket_status': ['New', 'InProgress', 'Draft'], 'category': 'SD-WAN',
                              'ticket_topic': 'VOO'}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        json.dumps(ticket_request_msg, default=str),
                                                        timeout=15)
        filtered_ticket_ids = []
        if all_tickets is not None and "tickets" in all_tickets.keys() and all_tickets["tickets"] is not None:
            filtered_ticket_ids = await self._filtered_ticket_details(all_tickets)
        else:
            self._logger.error(f'Tickets returned {json.dumps(all_tickets)}')
            slack_message = {'request_id': uuid(),
                             'message': f'Service outage triage: Error in ticket list. '
                                        f'Ticket list: {json.dumps(all_tickets)}. '
                                        f'Environment: {self._config.TRIAGE_CONFIG["environment"]}',
                             'response_topic': f'notification.slack.request.{self._service_id}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        for ticket_id in filtered_ticket_ids:
            id_by_serial = self._config.TRIAGE_CONFIG["id_by_serial"]
            edge_id = id_by_serial[ticket_id["serial"]]
            status_msg = {'request_id': uuid(),
                          'response_topic': f'edge.status.response.{self._service_id}',
                          'edge': edge_id}

            events_msg = {'request_id': uuid(),
                          'response_topic': f'alert.response.event.edge.{self._service_id}',
                          'edge': edge_id,
                          'start_date': (datetime.now(utc) - timedelta(days=7)),
                          'end_date': datetime.now(utc)}
            edge_status = await self._event_bus.rpc_request("edge.status.request",
                                                            json.dumps(status_msg, default=str), timeout=10)
            edge_events = await self._event_bus.rpc_request("alert.request.event.edge",
                                                            json.dumps(events_msg, default=str), timeout=10)
            ticket_dict = self._compose_ticket_note_object(edge_status, edge_events)
            if self._config.TRIAGE_CONFIG['environment'] == 'production':
                ticket_note = self._ticket_object_to_string(ticket_dict)
                ticket_append_note_msg = {'request_id': uuid(),
                                          'response_topic': f'bruin.ticket.note.append.response.{self._service_id}',
                                          'ticket_id': ticket_id["ticketID"],
                                          'note': ticket_note}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  json.dumps(ticket_append_note_msg),
                                                  timeout=15)
            elif self._config.TRIAGE_CONFIG['environment'] == 'dev':
                ticket_note = self._ticket_object_to_email_obj(ticket_dict)
                await self._event_bus.rpc_request("notification.email.request",
                                                  json.dumps(ticket_note),
                                                  timeout=10)
            slack_message = {'request_id': uuid(),
                             'message': f'Triage appeneded to ticket:'
                                        f'https://app.bruin.com/helpdesk?clientId=85940&ticketId='
                                        f'{ticket_id["ticketID"]} , in '
                                        f'{self._config.TRIAGE_CONFIG["environment"]}',
                             'response_topic': f'notification.slack.request.{self._service_id}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        self._logger.info("End of ticket polling job")

    async def _filtered_ticket_details(self, ticket_list):
        filtered_ticket_ids = []
        valid_serials = list(self._config.TRIAGE_CONFIG["id_by_serial"].keys())
        for ticket in ticket_list['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'response_topic': f'bruin.ticket.details.response.{self._service_id}',
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

    async def _check_for_new_events(self, timestamp, ticket_id):
        id_by_serial = self._config.TRIAGE_CONFIG["id_by_serial"]
        edge_id = id_by_serial[ticket_id["serial"]]
        events_msg = {'request_id': uuid(),
                      'response_topic': f'alert.response.event.edge.{self._service_id}',
                      'edge': edge_id,
                      'start_date': timestamp,
                      'end_date': datetime.now(timezone('US/Eastern'))}
        edge_events = await self._event_bus.rpc_request("alert.request.event.edge", json.dumps(
                                                                                events_msg, default=str), timeout=10)
        filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']

        event_list = [event for event in edge_events["events"]["data"] if event['event'] in filter_events_status_list]

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
                                              'response_topic': f'bruin.ticket.note.append.response.{self._service_id}',
                                              'ticket_id': ticket_id["ticketID"],
                                              'note': event_ticket_note}
                    await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                      json.dumps(ticket_append_note_msg),
                                                      timeout=15)
                    slack_message = {'request_id': uuid(),
                                     'message': f'Events appeneded to ticket:'
                                                f'https://app.bruin.com/helpdesk?clientId=85940&'
                                                f'ticketId={ticket_id["ticketID"]} , in '
                                                f'{self._config.TRIAGE_CONFIG["environment"]}',
                                     'response_topic': f'notification.slack.request.{self._service_id}'}
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
        edge_triage_dict["Edge URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/'

        edge_triage_dict["QoE URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/qoe/'

        edge_triage_dict["Transport URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/ \n'

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

        edge_triage_dict["Company Events URL"] = f'https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
                                                 f'operator/customer/' \
                                                 f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
                                                 f'/monitor/events/'
        edge_triage_dict["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                    ["data"], 'EDGE_UP')
        edge_triage_dict["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                     ["data"], 'EDGE_DOWN')
        edge_triage_dict["Last GE1 Interface Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                             ["events"]["data"],
                                                                                             'LINK_ALIVE',
                                                                                             'Link GE1 is no'
                                                                                             ' longer DEAD')
        edge_triage_dict["Last GE1 Interface Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                              ["events"]["data"],
                                                                                              'LINK_DEAD',
                                                                                              'Link GE1 is now DEAD')
        edge_triage_dict["Last GE2 Interface Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                             ["events"]["data"],
                                                                                             'LINK_ALIVE',
                                                                                             'Link GE2 is no'
                                                                                             ' longer DEAD')
        edge_triage_dict["Last GE2 Interface Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                              ["events"]["data"],
                                                                                              'LINK_DEAD',
                                                                                              'Link GE2 is now DEAD')
        edge_triage_dict["TimeStamp"] = datetime.now(timezone('US/Eastern'))
        return edge_triage_dict

    def _ticket_object_to_email_obj(self, ticket_dict):
        with open('src/templates/service_outage_triage.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', '1')
            email_html = email_html.replace('%%SERIAL_NUMBER%%', 'VC05200028729')

        overview_keys = ["Orchestrator instance", "Edge Name", "Edge URL", "QoE URL", "Transport URL", "Edge Status",
                         "Interface LABELMARK1", "Label LABELMARK2", "Interface GE1 Status", "Interface LABELMARK3",
                         "Interface GE2 Status", "Label LABELMARK4"]
        events_keys = ["Company Events URL", "Last Edge Online", "Last Edge Offline", "Last GE1 Interface Online",
                       "Last GE1 Interface Offline", "Last GE2 Interface Online", "Last GE2 Interface Offline"]
        edge_overview = OrderedDict()
        edge_events = OrderedDict()

        for key, value in ticket_dict.items():
            if key in overview_keys:
                edge_overview[key] = value
            if key in events_keys:
                edge_events[key] = value

        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            row = row.replace('%%KEY%%', parsed_key)
            row = row.replace('%%VALUE%%', str(edge_overview[key]))
            rows.append(row)
        email_html = email_html.replace('%%OVERVIEW_ROWS%%', "".join(rows))

        rows = []
        for idx, key in enumerate(edge_events.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(edge_events[key]))
            rows.append(row)
        email_html = email_html.replace('%%EVENT_ROWS%%', "".join(rows))

        return {
            'request_id': uuid(),
            'response_topic': f"notification.email.response.{self._service_id}",
            'email_data': {
                'subject': f'Service outage triage ({datetime.now().strftime("%Y-%m-%d")})',
                'recipient': self._config.TRIAGE_CONFIG["recipient"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [
                    {
                        'name': 'logo',
                        'data': base64.b64encode(open('src/templates/images/logo.png', 'rb').read()).decode('utf-8')
                    },
                    {
                        'name': 'header',
                        'data': base64.b64encode(open('src/templates/images/header.jpg', 'rb').read()).decode('utf-8')
                    },
                ],
                'attachments': []
            }
        }

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str
