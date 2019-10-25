import jinja2
from collections import OrderedDict
import re
from shortuuid import uuid
from datetime import datetime, timedelta
import base64


class TemplateRenderer:
    def __init__(self, service_id, config):
        self._config = config
        self._service_id = service_id

    def _find_recent_occurence_of_event(self, event_list, event_type, message=None):
        for event_obj in (i for i in event_list if isinstance(i, dict)):
            if event_obj['event'] == event_type:
                if message is not None:
                    if event_obj['message'] == message:
                        return event_obj['eventTime']
                else:
                    return event_obj['eventTime']
        return None

    def _compose_email_object(self, edges_status_to_report, edges_events_to_report, **kwargs):
        template_vars = {}
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        template = "src/templates/{}".format(kwargs.get("template", "service_outage_monitor.html"))
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)

        template_vars["__EDGE_COUNT__"] = '1'
        template_vars["__SERIAL_NUMBERS__"] = f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}'

        edge_overview = OrderedDict()

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
        edge_overview_keys = ["Interface LABELMARK1", "Label LABELMARK2", "Interface LABELMARK3", "Label LABELMARK4"]
        for i in edge_overview_keys:
            edge_overview[i] = None
        edge_overview["Line GE1 Status"] = "Line GE1 not available"
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

        edge_events = OrderedDict()

        edge_events["Company Events URL"] = f'https://{edges_status_to_report["edge_id"]["host"]}/#!/' \
                                            f'operator/customer/{edges_status_to_report["edge_id"]["enterprise_id"]}' \
                                            f'/monitor/events/'
        edge_events["Last Edge Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                               ["events"]["data"], 'EDGE_UP')
        edge_events["Last Edge Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                ["events"]["data"], 'EDGE_DOWN')
        edge_events["Last GE1 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                   ["events"]["data"], 'LINK_ALIVE',
                                                                                   'Link GE1 is no longer DEAD')
        edge_events["Last GE1 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                    ["events"]["data"],
                                                                                    'LINK_DEAD', 'Link GE1 is now DEAD')
        edge_events["Last GE2 Line Online"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                   ["events"]["data"],
                                                                                   'LINK_ALIVE',
                                                                                   'Link GE2 is no longer DEAD')
        edge_events["Last GE2 Line Offline"] = self._find_recent_occurence_of_event(edges_events_to_report
                                                                                    ["events"]["data"],
                                                                                    'LINK_DEAD',
                                                                                    'Link GE2 is now DEAD')
        rows = []
        for idx, key in enumerate(edge_overview.keys()):
            parsed_key = re.sub(r" LABELMARK(.)*", "", key)
            rows.append({
                "type": "even" if idx % 2 == 0 else "row",
                "__KEY__": parsed_key,
                "__VALUE__": str(edge_overview[key])
            })
        template_vars["__OVERVIEW_ROWS__"] = rows
        rows = []
        for idx, key in enumerate(edge_events.keys()):
            rows.append({
                "type": "even" if idx % 2 == 0 else "row",
                "__KEY__": key,
                "__VALUE__": str(edge_events[key])
            })
        template_vars["__EVENT_ROWS__"] = rows
        email_html = templ.render(**template_vars)
        return {
            'request_id': uuid(),
            'response_topic': f"notification.email.response.{self._service_id}",
            'email_data': {
                'subject': f'Service outage monitor ({datetime.now().strftime("%Y-%m-%d")})',
                'recipient': self._config.MONITOR_CONFIG["recipient"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [
                    {
                        'name': 'logo',
                        'data': base64.b64encode(open(logo, 'rb').read()).decode('utf-8')
                    },
                    {
                        'name': 'header',
                        'data': base64.b64encode(open(header, 'rb').read()).decode('utf-8')
                    },
                ],
                'attachments': []
            }
        }
