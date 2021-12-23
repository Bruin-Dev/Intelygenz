import os
import jinja2
import base64
from shortuuid import uuid
from datetime import datetime
from pytz import timezone

DATE_FORMAT = '%Y-%m-%d'


class TemplateRepository:
    def __init__(self, config):
        self._config = config

    def _build_email(self, client_id, subject, template, template_vars, recipients=None):
        logo = 'src/templates/images/logo.png'
        header = 'src/templates/images/header.jpg'

        template = os.path.join('src', 'templates', template)
        template_loader = jinja2.FileSystemLoader(searchpath='.')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template)

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': subject,
                'recipient': recipients or self._get_recipients(client_id),
                'text': '',
                'html': template.render(**template_vars),
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

    def _get_recipients(self, client_id):
        recipients = self._config.REPORT_RECIPIENTS['default']

        if client_id in self._config.REPORT_RECIPIENTS:
            recipients = recipients + self._config.REPORT_RECIPIENTS[client_id]

        return ', '.join(recipients)

    def compose_monitor_report_email(self, client_id, client_name, report_items):
        template = 'service_affecting_monitor_report.html'
        template_vars = {}
        rows = []

        for index, item in enumerate(report_items):
            rows.append({
                'type': self._get_row_type(index),
                '__KEY__': item['serial_number'],
                '__CLIENT__': f"{item['customer']['client_id']} | {item['customer']['client_name']}",
                '__EDGE_NAME__': item['edge_name'],
                '__LOCATION__': '<br>'.join(list(item['location'].values())),
                '__NUMBER_OF_TICKETS__': item['number_of_tickets'],
                '__BRUIN_TICKETS_ID__': ',<br>'.join([str(_id) for _id in item['bruin_tickets_id']]),
                '__INTERFACES__': str(item['interfaces']),
                '__TROUBLE__': str(item['trouble']),
            })

        if rows:
            now = datetime.now(timezone(self._config.MONITOR_REPORT_CONFIG['timezone']))
            date = now.strftime(DATE_FORMAT)
            subject = f'{client_name} - Reoccurring Service Affecting Trouble - {date}'

            template_vars['__DATE__'] = date
            template_vars['__YEAR__'] = now.year
            template_vars['__CLIENT_ID__'] = client_id
            template_vars['__CLIENT_NAME__'] = client_name
            template_vars['__OVERVIEW_ROWS__'] = rows

            return self._build_email(client_id=client_id, subject=subject, template=template,
                                     template_vars=template_vars)

    def compose_bandwidth_report_email(self, client_id, client_name, report_items):
        template = 'bandwidth_report.html'
        template_vars = {}
        rows = []

        for index, item in enumerate(report_items):
            rows.append({
                'type': self._get_row_type(index),
                '__SERIAL__': item['serial_number'],
                '__CLIENT__': f"{client_id} | {client_name}",
                '__EDGE_NAME__': item['edge_name'],
                '__INTERFACE__': item['interface'],
                '__BANDWIDTH__': item['bandwidth'],
                '__THRESHOLD_EXCEEDED__': item['threshold_exceeded'],
                '__TICKET_IDS__': ',<br>'.join([str(_id) for _id in item['ticket_ids']]),
            })

        if rows:
            now = datetime.now(timezone(self._config.BANDWIDTH_REPORT_CONFIG['timezone']))
            date = now.strftime(DATE_FORMAT)
            subject = f'{client_name} - Daily Bandwidth Report - {date}'

            template_vars['__DATE__'] = date
            template_vars['__YEAR__'] = now.year
            template_vars['__CLIENT_ID__'] = client_id
            template_vars['__CLIENT_NAME__'] = client_name
            template_vars['__ROWS__'] = rows

            return self._build_email(client_id=client_id, subject=subject, template=template,
                                     template_vars=template_vars, recipients='mettel.automation@intelygenz.com')

    @staticmethod
    def _get_row_type(index):
        return 'even' if index % 2 == 0 else 'odd'
