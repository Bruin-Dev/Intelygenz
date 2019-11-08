import base64
import json
import re
from collections import OrderedDict
from datetime import datetime

from shortuuid import uuid

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


class DevelopmentAction:

    def __init__(self, event_bus, config):
        self._event_bus = event_bus
        self._config = config

    async def run_triage_action(self, ticket_dict, ticket_id):
        ticket_note = self._ticket_object_to_email_obj(ticket_dict)
        await self._event_bus.rpc_request("notification.email.request",
                                          json.dumps(ticket_note),
                                          timeout=10)
        slack_message = {'request_id': uuid(),
                         'message': f'Triage appended to ticket: '
                                    f'https://app.bruin.com/helpdesk?clientId=85940&ticketId='
                                    f'{ticket_id}, in '
                                    f'{self._config.TRIAGE_CONFIG["environment"]}'}
        await self._event_bus.rpc_request("notification.slack.request", json.dumps(slack_message), timeout=10)

    async def run_event_action(self, event_note, ticket_id):
        pass

    def _ticket_object_to_email_obj(self, ticket_dict):
        with open('src/templates/service_outage_triage.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%EDGE_COUNT%%', '1')
            email_html = email_html.replace('%%SERIAL_NUMBER%%', 'VC05200028729')

        overview_keys = ["Orchestrator instance", "Edge Name", "Links", "Edge Status",
                         "Interface LABELMARK1", "Label LABELMARK2", "Interface GE1 Status", "Interface LABELMARK3",
                         "Interface GE2 Status", "Label LABELMARK4"]
        events_keys = ["Last Edge Online", "Last Edge Offline", "Last GE1 Interface Online",
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
