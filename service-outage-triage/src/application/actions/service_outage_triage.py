import json
import re
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta

from apscheduler.util import undefined
from dateutil.parser import parse
from pytz import timezone, utc
from shortuuid import uuid

from igz.packages.eventbus.eventbus import EventBus


class ServiceOutageTriage:

    def __init__(self, event_bus: EventBus, logger, scheduler, config, template_renderer, outage_utils):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._template_renderer = template_renderer
        self._outage_utils = outage_utils

    async def start_service_outage_triage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: service outage triage configured to run every '
                          f'{self._config.TRIAGE_CONFIG["polling_minutes"]} minutes')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._poll_tickets, 'interval', minutes=self._config.TRIAGE_CONFIG["polling_minutes"],
                                next_run_time=next_run_time,
                                replace_existing=True, id='_service_outage_triage_process')

    async def _poll_tickets(self):
        self._logger.info(f'Creating dict of serial to monitor using '
                          f'filter {self._config.TRIAGE_CONFIG["velo_filter"]}')
        client_id_to_list_of_serial_dict = await self._create_client_id_to_dict_of_serials_dict()

        self._logger.info("Requesting tickets from Bruin")
        ticket_response = dict()
        for client_id in client_id_to_list_of_serial_dict:
            try:
                self._logger.info(f'Requesting tickets for Bruin company of client_id: {client_id}')
                request_tickets_message = {'request_id': uuid(), 'client_id': client_id,
                                           'ticket_status': ['New', 'InProgress', 'Draft'],
                                           'params': {'client_id': client_id,
                                                      'category': 'SD-WAN',
                                                      'ticket_topic': 'VOO'}
                                           }
                ticket_response = await self._event_bus.rpc_request("bruin.ticket.request",
                                                                    request_tickets_message,
                                                                    timeout=90)
                if ticket_response is None or "tickets" not in ticket_response.keys() or type(
                        ticket_response["tickets"]) is not list:
                    self._logger.error(f'Ticket data doesn\'t comply with format in {json.dumps(ticket_response)}')
                    slack_message = {'request_id': uuid(),
                                     'message': f'Service outage triage: Error: ticket list does not comply in format. '
                                     f'Ticket list: {json.dumps(ticket_response)}. '
                                     f'Company Bruin ID: {client_id}. '
                                     f'Environment: {self._config.TRIAGE_CONFIG["environment"]}'}
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
                    continue
                self._logger.info(f'Tickets for company of client_id: {client_id} retrieved correctly')

            except Exception:
                self._logger.error(f'Error trying to get tickets for Bruin company of client_id:: {client_id}')
                slack_message = {'request_id': uuid(),
                                 'message': f'Service outage triage: Unknown error getting ticket list. '
                                 f'Company Bruin ID: {client_id}. '
                                 f'Environment: {self._config.TRIAGE_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

            filtered_ticket_ids = await self._filtered_ticket_details(ticket_response,
                                                                      client_id,
                                                                      client_id_to_list_of_serial_dict[client_id])

            for ticket_id in filtered_ticket_ids:
                self._logger.info(f"Triaging ticket id: {ticket_id['ticketID']} in client_id: {client_id}")
                edge_status = client_id_to_list_of_serial_dict[client_id][ticket_id["serial"]]
                edge_id = edge_status["edge_id"]

                filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
                events_msg = {
                    'request_id': uuid(),
                    "body":
                        {

                            'edge': edge_id,
                            'start_date': (datetime.now(utc) - timedelta(days=7)),
                            'end_date': datetime.now(utc),
                            'filter': filter_events_status_list
                        }
                }

                edge_events = await self._event_bus.rpc_request("alert.request.event.edge", events_msg, timeout=180)
                ticket_dict = self._compose_ticket_note_object(edge_status, edge_events)
                if self._config.TRIAGE_CONFIG['environment'] == 'production':
                    ticket_note = self._ticket_object_to_string(ticket_dict)
                    ticket_append_note_msg = {'request_id': uuid(),
                                              'ticket_id': ticket_id["ticketID"],
                                              'note': ticket_note}
                    await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                      ticket_append_note_msg,
                                                      timeout=15)
                elif self._config.TRIAGE_CONFIG['environment'] == 'dev':
                    ticket_note = self._template_renderer._ticket_object_to_email_obj(ticket_dict)
                    await self._event_bus.rpc_request("notification.email.request", ticket_note, timeout=10)
                slack_message = {'request_id': uuid(),
                                 'message': f'Triage appended to ticket: '
                                 f'https://app.bruin.com/helpdesk?clientId={client_id}&ticketId='
                                 f'{ticket_id["ticketID"]}, in '
                                 f'{self._config.TRIAGE_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
        self._logger.info("End of ticket polling job")

    async def _filtered_ticket_details(self, ticket_list, company_id, edge_serial_list):
        filtered_ticket_ids = []
        valid_serials = edge_serial_list.keys()
        for ticket in ticket_list['tickets']:
            ticket_detail_msg = {'request_id': uuid(),
                                 'ticket_id': ticket['ticketID']}
            ticket_details = await self._event_bus.rpc_request("bruin.ticket.details.request",
                                                               ticket_detail_msg,
                                                               timeout=15)
            for ticket_detail in ticket_details['ticket_details']['ticketDetails']:
                triage_exists = False
                if 'detailValue' in ticket_detail.keys():
                    if ticket_detail['detailValue'] in valid_serials:
                        ticket_item = dict()
                        # add edge_status to ticket[item]
                        ticket_item["client_id"] = company_id
                        ticket_item["edge_status"] = edge_serial_list[ticket_detail['detailValue']]
                        ticket_item["ticketID"] = ticket['ticketID']
                        ticket_item["serial"] = ticket_detail['detailValue']
                        ticket_item['notes'] = ticket_details['ticket_details']['ticketNotes']
                        sorted_ticket_notes = sorted(ticket_details['ticket_details']['ticketNotes'],
                                                     key=lambda note: note['createdDate'], reverse=True)

                        for ticket_note in sorted_ticket_notes:
                            if ticket_note['noteValue'] is not None:
                                if '#*Automation Engine*#' in ticket_note['noteValue']:
                                    self._logger.info(f'Triage already exists for ticket id of {ticket["ticketID"]}')
                                    if 'TimeStamp: ' in ticket_note['noteValue']:
                                        last_timestamp = self._extract_field_from_string(ticket_note['noteValue'],
                                                                                         "TimeStamp: ")
                                        timestamp_difference = datetime.now(timezone(
                                            self._config.TRIAGE_CONFIG['timezone'])
                                        ) - parse(last_timestamp)
                                        if timestamp_difference > timedelta(minutes=30):
                                            await self._check_for_new_events(last_timestamp, ticket_item)
                                    triage_exists = True
                                    break
                        if not triage_exists:
                            filtered_ticket_ids.append(ticket_item)

                        await self._auto_resolve_tickets(ticket_item, ticket_detail['detailID'])

                        break
        return filtered_ticket_ids

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in event_list:
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        time = parse(event_obj['eventTime'])
                        return time.astimezone(timezone(self._config.TRIAGE_CONFIG['timezone']))
                else:
                    time = parse(event_obj['eventTime'])
                    return time.astimezone(timezone(self._config.TRIAGE_CONFIG['timezone']))
        return None

    def _extract_field_from_string(self, dict_as_string, key1, key2='#DEFAULT_END#'):
        return dict_as_string[dict_as_string.find(key1) + len(key1): dict_as_string.find(key2)]

    def _client_id_from_edge_status(self, edge_status):
        # If there's no Bruin enterprise ID hardcoded in velocloud name we use Mettel's ID instead
        client_id = 9994
        if "edge_info" in edge_status.keys() and "enterprise_name" in edge_status['edge_info'].keys():
            if len(edge_status['edge_info']['enterprise_name'].split('|')) is 3:
                # If there's a Bruin client ID in velocloud it will look like 'enterprise |112|'
                # 112 would be Bruin enterprise ID in this case.
                client_id = edge_status['edge_info']['enterprise_name'].split('|')[1]
        return client_id

    async def _check_for_new_events(self, timestamp, ticket_id):
        edge_status = ticket_id["edge_status"]
        edge_id = edge_status["edge_id"]
        filter_events_status_list = ['EDGE_UP', 'EDGE_DOWN', 'LINK_ALIVE', 'LINK_DEAD']
        events_msg = {'request_id': uuid(),
                      "body": {
                          'edge': edge_id,
                          'start_date': timestamp,
                          'end_date': datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone'])),
                          'filter': filter_events_status_list}
                      }

        client_id = ticket_id["client_id"]
        edge_events = await self._event_bus.rpc_request("alert.request.event.edge", events_msg, timeout=180)

        event_list = edge_events['events']

        if len(event_list) > 0:
            sorted_event_list = sorted(event_list, key=lambda event: event['eventTime'])

            split_event_lists = [sorted_event_list[i:i + self._config.TRIAGE_CONFIG['event_limit']]
                                 for i in range(0, len(sorted_event_list), self._config.TRIAGE_CONFIG['event_limit'])]
            for events in split_event_lists:
                event_obj = self._compose_event_note_object(events)
                event_timestamp = parse(events[len(events) - 1]["eventTime"]).astimezone(timezone(
                    self._config.TRIAGE_CONFIG['timezone']))
                event_ticket_note = "#*Automation Engine*#" + event_obj + 'TimeStamp: ' + str(
                    event_timestamp + timedelta(seconds=1))
                if self._config.TRIAGE_CONFIG['environment'] == 'production':
                    ticket_append_note_msg = {'request_id': uuid(),
                                              'ticket_id': ticket_id["ticketID"],
                                              'note': event_ticket_note}
                    await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                      ticket_append_note_msg,
                                                      timeout=15)
                    slack_message = {'request_id': uuid(),
                                     'message': f'Events appended to ticket: '
                                     f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                     f'ticketId={ticket_id["ticketID"]}, in '
                                     f'{self._config.TRIAGE_CONFIG["environment"]}'}
                    await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)
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
            event_time = parse(event["eventTime"]).astimezone(timezone(self._config.TRIAGE_CONFIG["timezone"]))
            event_str = event_str + f'eventTime: {event_time}\n'
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
        edge_triage_dict["TimeStamp"] = datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone']))
        return edge_triage_dict

    def _ticket_object_to_string(self, ticket_dict):
        edge_triage_str = "#*Automation Engine*# \n"
        for key in ticket_dict.keys():
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            edge_triage_str = edge_triage_str + f'{parsed_key}: {ticket_dict[key]} \n'
        return edge_triage_str

    async def _auto_resolve_tickets(self, ticket_id, detail_id):
        if ticket_id["serial"] not in self._config.TRIAGE_CONFIG["autoresolve_serials_whitelist"]:
            return
        self._logger.info(f'Checking autoresolve for ticket id {json.dumps(ticket_id, indent=2, default=str)}')

        id_by_serial = self._config.TRIAGE_CONFIG["id_by_serial"]
        edge_id = id_by_serial[ticket_id["serial"]]

        if not self._outage_utils.is_outage_ticket_auto_resolvable(ticket_id['ticketID'], ticket_id['notes'], 3):
            self._logger.info("Cannot autoresolved due to ticket being autoresolved more than 3 times")
            return

        status_msg = {'request_id': uuid(),
                      'body': edge_id}
        edge_status = await self._event_bus.rpc_request("edge.status.request", status_msg,
                                                        timeout=45)
        edge_info = edge_status['edge_info']

        filter_events_status_list = ['EDGE_DOWN', 'LINK_DEAD']

        events_msg = {'request_id': uuid(),
                      'body': {
                          'edge': edge_id,
                          'start_date': datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone'])) - timedelta(
                              minutes=45),
                          'end_date': datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone'])),
                          'filter': filter_events_status_list}
                      }

        edge_events = await self._event_bus.rpc_request("alert.request.event.edge", events_msg, timeout=180)

        self._logger.info(f'Received event list of {json.dumps(edge_events, indent=2, default=str)} from velocloud')

        if len(edge_events["events"]) == 0:
            self._logger.info("Too much time has passed for an auto-resolve. No down events have occurred in the "
                              "last 45 minutes")
            return

        if self._outage_utils.is_there_an_outage(edge_info) is False:
            self._logger.info(f'Autoresolving ticket of ticket id: {json.dumps(ticket_id, indent=2, default=str)}')

            if self._config.TRIAGE_CONFIG['environment'] == 'production':
                resolve_ticket_msg = {'request_id': uuid(),
                                      'ticket_id': ticket_id['ticketID'],
                                      'detail_id': detail_id
                                      }

                resolve_note_msg = "#*Automation Engine*#\nAuto-resolving ticket.\n" + 'TimeStamp: ' + str(
                    datetime.now(timezone(
                        self._config.TRIAGE_CONFIG['timezone'])) + timedelta(seconds=1))
                ticket_append_note_msg = {'request_id': uuid(),
                                          'ticket_id': ticket_id["ticketID"],
                                          'note': resolve_note_msg}

                await self._event_bus.rpc_request("bruin.ticket.status.resolve",
                                                  resolve_ticket_msg,
                                                  timeout=15)

                await self._event_bus.rpc_request("bruin.ticket.note.append.request",
                                                  ticket_append_note_msg,
                                                  timeout=15)

                client_id = self._client_id_from_edge_status(edge_status)
                slack_message = {'request_id': uuid(),
                                 'message': f'Ticket autoresolved '
                                 f'https://app.bruin.com/helpdesk?clientId={client_id}&'
                                 f'ticketId={ticket_id["ticketID"]}, in '
                                 f'{self._config.TRIAGE_CONFIG["environment"]}'}
                await self._event_bus.rpc_request("notification.slack.request", slack_message, timeout=10)

            self._logger.info(f"Ticket of ticketID:{ticket_id['ticketID']} auto-resolved")

    async def _create_client_id_to_dict_of_serials_dict(self):
        client_id_to_dict_of_serial_dict = defaultdict(dict)
        self._logger.info("Requesting edge list")
        list_request = dict(request_id=uuid(), body={'filter': self._config.TRIAGE_CONFIG["velo_filter"]})
        edge_list = await self._event_bus.rpc_request("edge.list.request", list_request, timeout=200)
        self._logger.info(f'Edge list received from event bus')
        edge_status_requests = [
            {'request_id': edge_list["request_id"], 'body': edge} for edge in edge_list["body"]]
        self._logger.info("Processing all edges and building dictionary of clients to a dict of serials")
        for request in edge_status_requests:
            self._logger.info(f"Processing edge request: {request}")
            edge_status = await self._event_bus.rpc_request("edge.status.request", request, timeout=120)
            if edge_status["status"] in range(200, 300):
                client_id = self._client_id_from_edge_status(edge_status)
                edge_info = edge_status["body"]["edge_info"]
                client_id_to_dict_of_serial_dict[client_id][edge_info["edges"]["serialNumber"]] = edge_status
            else:
                self._logger.info(f"Not edge status for {request}")

        return client_id_to_dict_of_serial_dict
