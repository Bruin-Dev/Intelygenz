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
        self._logger.info(f'Scheduled task: edge monitoring process configured to run each first hour each day')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone('US/Eastern'))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._poll_tickets, 'interval', minute=1, next_run_time=next_run_time,
                                replace_existing=True, id='_service_outage_triage_process')

    async def _poll_tickets(self):
        self._logger.info("Requesting tickets from Bruin")
        ticket_request_msg = {'request_id': uuid(), 'response_topic': f'bruin.ticket.response.{self._service_id}',
                              'client_id': 85940}
        all_tickets = await self._event_bus.rpc_request("bruin.ticket.request",
                                                        json.dumps(ticket_request_msg, default=str),
                                                        timeout=10)
        for ticket in all_tickets['tickets']['responses']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'response_topic': f'bruin.ticket.details.response.{self._service_id}',
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               json.dumps(ticket_detail_msg, default=str),
                                                               timeout=10)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                if ticket_detail['detailValue'] == 'VC05200028729':
                    triage_exists = False
                    for ticket_note in ticket_details['ticket_details']['ticketNotes']:
                        if ticket_note['noteValue'] is not None:
                            if '#*Automaton Engine*#' in ticket_note['noteValue']:
                                triage_exists = True
                                break
                    if triage_exists is True:
                        break
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
                    ticket_note = self._compose_ticket_note_object(edge_status, edge_events)
                    ticket_append_note_msg = {'request_id': uuid(),
                                              'response_topic': f'bruin.ticket.note.append.response.{self._service_id}',
                                              'ticket_id': ticket['ticketID'],
                                              'ticket_note': json.dumps(ticket_note, default=str)}
                    ticket_append_note = await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                                           json.dumps(ticket_append_note_msg),
                                                                           timeout=10)

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

        edge_overview = OrderedDict()

        edge_overview["#*Automaton Engine*#"] = ''
        edge_overview["Orchestrator instance"] = edges_status_to_report['edge_id']['host']
        edge_overview["Edge Name"] = edges_status_to_report["edge_info"]["edges"]["name"]
        edge_overview["Edge URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/'

        edge_overview["QoE URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/qoe/'

        edge_overview["Transport URL"] = \
            f'https://{edges_status_to_report["edge_id"]["host"]}/#!/operator/customer/' \
            f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
            f'/monitor/edge/{edges_status_to_report["edge_id"]["edge_id"]}/links/'

        edge_overview["Edge Status"] = edges_status_to_report["edge_info"]["edges"]["edgeState"]

        edge_overview["Interface LABELMARK1"] = None
        edge_overview["Label LABELMARK2"] = None
        edge_overview["Line GE1 Status"] = "Line GE1 not available"

        edge_overview["Interface LABELMARK3"] = None
        edge_overview["Label LABELMARK4"] = None
        edge_overview["Line GE2 Status"] = "Line GE2 not available"

        link_data = dict()

        link_data["GE1"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE1"]
        link_data["GE2"] = [link for link in edges_status_to_report["edge_info"]["links"]
                            if link["link"] is not None
                            if link["link"]["interface"] == "GE2"]
        if len(link_data["GE1"]) > 0:
            edge_overview["Interface LABELMARK1"] = link_data["GE1"][0]["link"]["interface"]
            edge_overview["Line GE1 Status"] = link_data["GE1"][0]["link"]["state"]
            edge_overview["Label LABELMARK2"] = link_data["GE1"][0]["link"]['displayName']
        if len(link_data["GE2"]) > 0:
            edge_overview["Interface LABELMARK3"] = link_data["GE2"][0]["link"]["interface"]
            edge_overview["Line GE2 Status"] = link_data["GE2"][0]["link"]["state"]
            edge_overview["Label LABELMARK4"] = link_data["GE2"][0]["link"]['displayName']

        edge_overview["Company Events URL"] = f'https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
                                              f'operator/customer/' \
                                              f'{edges_status_to_report["edge_id"]["enterprise_id"]}' \
                                              f'/monitor/events/'
        edge_overview["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                 ["data"], 'EDGE_UP')
        edge_overview["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                  ["data"], 'EDGE_DOWN')
        edge_overview["Last GE1 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                     ["data"], 'LINK_ALIVE',
                                                                                     'Link GE1 is no longer DEAD')
        edge_overview["Last GE1 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                      ["data"], 'LINK_DEAD',
                                                                                      'Link GE1 is now DEAD')
        edge_overview["Last GE2 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                     ["data"], 'LINK_ALIVE',
                                                                                     'Link GE2 is no longer DEAD')
        edge_overview["Last GE2 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report["events"]
                                                                                      ["data"], 'LINK_DEAD',
                                                                                      'Link GE2 is now DEAD')
        return edge_overview
