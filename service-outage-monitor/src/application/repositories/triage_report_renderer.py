import base64

from collections import OrderedDict
from datetime import datetime

from pytz import timezone
from shortuuid import uuid


class TriageReportRenderer:
    __report_template_filename = "triage_report.html"
    __logo_path = "src/templates/images/logo.png"
    __header_path = "src/templates/images/header.jpg"

    def __init__(self, config, templates_environment):
        self._config = config
        self._templates_environment = templates_environment

    def compose_email_object(self, ticket_data):
        overview_data = OrderedDict({
            'Orchestrator Instance': ticket_data.get('Orchestrator Instance'),
            'Edge Name': ticket_data.get('Edge Name'),
            'Edge Status': ticket_data.get('Edge Status'),
        })
        overview_data['Links'] = ' - '.join(
            f'<a href="{url}">{name}</a>' for name, url in ticket_data.get("Links").items()
        )

        events_data = OrderedDict()

        for key, value in ticket_data.items():
            if key.startswith('Interface'):
                overview_data[key] = value
            elif key == 'Last Edge Offline' or key == 'Last Edge Online':
                events_data[key] = value
            elif key.startswith('Last') and (key.endswith('Interface Offline') or key.endswith('Interface Online')):
                events_data[key] = value

        overview_rows = []
        for index, (key, value) in enumerate(overview_data.items()):
            overview_rows.append({
                "type": "even" if index % 2 == 0 else "odd",
                "__KEY__": key,
                "__VALUE__": str(value),
            })

        event_rows = []
        for index, (key, value) in enumerate(events_data.items()):
            event_rows.append({
                "type": "even" if index % 2 == 0 else "odd",
                "__KEY__": key,
                "__VALUE__": str(value)
            })

        current_datetime = datetime.now(timezone(self._config.TRIAGE_CONFIG['timezone']))

        template_vars = {
            "__SERIAL_NUMBER__": ticket_data.get('Serial'),
            "__OVERVIEW_ROWS__": overview_rows,
            "__EVENT_ROWS__": event_rows,
            "__CURRENT_YEAR__": current_datetime.year,
        }

        template = self._templates_environment.get_template(self.__report_template_filename)
        email_html = template.render(template_vars)

        return {
                'request_id': uuid(),
                'email_data': {
                    'subject': f'Service outage triage ({current_datetime})',
                    'recipient': self._config.TRIAGE_CONFIG["recipient"],
                    'text': 'this is the accessible text for the email',
                    'html': email_html,
                    'images': [
                        {
                            'name': 'logo',
                            'data': base64.b64encode(open(self.__logo_path, 'rb').read()).decode('utf-8')
                        },
                        {
                            'name': 'header',
                            'data': base64.b64encode(open(self.__header_path, 'rb').read()).decode('utf-8')
                        },
                    ],
                    'attachments': []
                }
            }
