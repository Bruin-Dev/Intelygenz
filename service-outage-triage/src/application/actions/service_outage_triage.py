import base64

import json
import re
from collections import OrderedDict
from datetime import datetime, timedelta

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
                              'client_id': 85940, 'ticket_status': ['New', 'InProgress'], 'category': 'SD-WAN'}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        json.dumps(ticket_request_msg, default=str),
                                                        timeout=10)
        filtered_ticket_ids = []
        if all_tickets is not None and "tickets" in all_tickets.keys() and all_tickets["tickets"] is not None:
            filtered_ticket_ids = await self._filtered_ticket_details(all_tickets)
        else:
            self._logger.error(f'Tickets returned {json.dumps(all_tickets)}')
            slack_message = {'request_id': uuid(),
                             'message': f'{json.dumps(all_tickets)}',
                             'response_topic': f'notification.slack.request.{self._service_id}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        for ticket_id in filtered_ticket_ids:
            edge_id = {"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1602}
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
                                          'ticket_id': ticket_id,
                                          'note': ticket_note}
                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  json.dumps(ticket_append_note_msg),
                                                  timeout=10)
            elif self._config.TRIAGE_CONFIG['environment'] == 'dev':
                ticket_note = self._ticket_object_to_email_obj(ticket_dict)
                await self._event_bus.rpc_request("notification.email.request",
                                                  json.dumps(ticket_note),
                                                  timeout=10)
            slack_message = {'request_id': uuid(),
                             'message': f'Triage appeneded to ticket:'
                                        f'https://app.bruin.com/helpdesk?clientId=88089&ticketId={ticket_id} , in '
                                        f'{self._config.TRIAGE_CONFIG["environment"]}',
                             'response_topic': f'notification.slack.request.{self._service_id}'}
            await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)
        self._logger.info("End of ticket polling job")

    async def _filtered_ticket_details(self, ticket_list):
        filtered_ticket_ids = []
        if ticket_list["tickets"] is not None:
            self._logger.info(f'List of tickets length: {len(ticket_list["tickets"])}')
        for ticket in ticket_list['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'response_topic': f'bruin.ticket.details.response.{self._service_id}',
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               json.dumps(ticket_detail_msg, default=str),
                                                               timeout=10)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                triage_exists = False
                if 'detailValue' in ticket_detail.keys():
                    if 'VC05200028729' in ticket_detail['detailValue']:
                        for ticket_note in ticket_details['ticket_details']['ticketNotes']:
                            if ticket_note['noteValue'] is not None:
                                if '#*Automation Engine*#' in ticket_note['noteValue']:
                                    self._logger.info(f'Triage already exists for ticket id of {ticket["ticketID"]}')
                                    triage_exists = True
                        if triage_exists is not True:
                            filtered_ticket_ids.append(ticket['ticketID'])
                            break
        return filtered_ticket_ids

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in event_list:
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        return event_obj['eventTime']
                else:
                    return event_obj['eventTime']
        return None

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
        edge_triage_dict["Line GE1 Status"] = "Line GE1 not available"

        edge_triage_dict["Interface LABELMARK3"] = None
        edge_triage_dict["Label LABELMARK4"] = None
        edge_triage_dict["Line GE2 Status"] = "Line GE2 not available\n"

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
            edge_triage_dict["Line GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_triage_dict["Label LABELMARK2"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_triage_dict["Interface LABELMARK3"] = link_data["GE2"][0]["link"]["interface"]
            edge_triage_dict["Line GE2 Status"] = f'{link_data["GE2"][0]["link"]["state"]}\n'
            edge_triage_dict["Label LABELMARK4"] = link_data["GE2"][0]["link"]['displayName']

        edge_triage_dict["Company Events URL"] = f'https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
                                                 f'operator/customer/' \
                                                 f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
                                                 f'/monitor/events/'
        edge_triage_dict["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                    ["data"], 'EDGE_UP')
        edge_triage_dict["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                     ["data"], 'EDGE_DOWN')
        edge_triage_dict["Last GE1 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                        ["data"], 'LINK_ALIVE',
                                                                                        'Link GE1 is no longer DEAD')
        edge_triage_dict["Last GE1 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                         ["events"]["data"],
                                                                                         'LINK_DEAD',
                                                                                         'Link GE1 is now DEAD')
        edge_triage_dict["Last GE2 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                        ["data"], 'LINK_ALIVE',
                                                                                        'Link GE2 is no longer DEAD')
        edge_triage_dict["Last GE2 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                         ["events"]["data"],
                                                                                         'LINK_DEAD',
                                                                                         'Link GE2 is now DEAD')
        return edge_triage_dict

    def _ticket_object_to_email_obj(self, ticket_dict):
        with open('src/templates/service_outage_triage.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', '1')
            email_html = email_html.replace('%%SERIAL_NUMBER%%', 'VC05200028729')

        overview_keys = ["Orchestrator instance", "Edge Name", "Edge URL", "QoE URL", "Transport URL", "Edge Status",
                         "Interface LABELMARK1", "Label LABELMARK2", "Line GE1 Status", "Interface LABELMARK3",
                         "Line GE2 Status", "Label LABELMARK4"]
        events_keys = ["Company Events URL", "Last Edge Online", "Last Edge Offline", "Last GE1 Line Online",
                       "Last GE1 Line Offline", "Last GE2 Line Online", "Last GE2 Line Offline"]
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
