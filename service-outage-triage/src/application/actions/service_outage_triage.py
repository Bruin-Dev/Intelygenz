import json
from collections import OrderedDict
from datetime import datetime, timedelta

from apscheduler.util import undefined
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


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
        self._scheduler.add_job(self._poll_tickets, 'interval', seconds=60, next_run_time=next_run_time,
                                replace_existing=True, id='_service_outage_triage_process')

    async def _poll_tickets(self):
        self._logger.info("Requesting tickets from Bruin")
        ticket_request_msg = {'request_id': uuid(), 'response_topic': f'bruin.ticket.response.{self._service_id}',
                              'client_id': 85940, 'ticket_status': ['New', 'In-Progress'], 'category': 'SD-WAN'}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        json.dumps(ticket_request_msg, default=str),
                                                        timeout=10)
        filtered_ticket_ids = await self._filtered_ticket_details(all_tickets)

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
            ticket_note = self._ticket_object_to_string(ticket_dict)
            if self._config.TRIAGE_CONFIG['environment'] == 'production':
                ticket_append_note_msg = {'request_id': uuid(),
                                          'response_topic': f'bruin.ticket.note.append.response.{self._service_id}',
                                          'ticket_id': ticket_id,
                                          'note': ticket_note}
                ticket_append_note = await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                                       json.dumps(ticket_append_note_msg),
                                                                       timeout=10)
            elif self._config.TRIAGE_CONFIG['environment'] == 'dev':
                ticket_append_note_msg = {'request_id': uuid(),
                                          'response_topic': f'notification.slack.response.{self._service_id}',
                                          'message': ticket_note}
                ticket_send_to_slack = await self._event_bus.rpc_request("notification.slack.request",
                                                                         json.dumps(ticket_append_note_msg),
                                                                         timeout=10)
        self._logger.info("End of ticket polling job")

    async def _filtered_ticket_details(self, ticket_list):
        filtered_ticket_ids = []
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
                                if '#*Automaton Engine*#' in ticket_note['noteValue']:
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
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/'

        edge_triage_dict["Edge Status"] = edges_status_to_report["edge_info"]["edges"]["edgeState"]

        edge_triage_dict["Interface LABELMARK1"] = None
        edge_triage_dict["Label LABELMARK2"] = None
        edge_triage_dict["Line GE1 Status"] = "Line GE1 not available"

        edge_triage_dict["Interface LABELMARK3"] = None
        edge_triage_dict["Label LABELMARK4"] = None
        edge_triage_dict["Line GE2 Status"] = "Line GE2 not available"

        link_data = dict()

        link_data["GE1"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE1"]
        link_data["GE2"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE2"]
        if len(link_data["GE1"]) > 0:
            edge_triage_dict["Interface LABELMARK1"] = link_data["GE1"][0]["link"]["interface"]
            edge_triage_dict["Line GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_triage_dict["Label LABELMARK2"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_triage_dict["Interface LABELMARK3"] = link_data["GE2"][0]["link"]["interface"]
            edge_triage_dict["Line GE2 Status"] = link_data["GE2"][0]["link"]["state"]
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

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automaton Engine*#| "
        for key in ticket_dict.keys():
            edge_triage_str = edge_triage_str + f'{key}: {ticket_dict[key]} |'
        return edge_triage_str
