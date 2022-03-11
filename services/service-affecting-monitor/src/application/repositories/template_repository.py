import os
import csv
import jinja2
import base64
from io import StringIO
from shortuuid import uuid
from datetime import datetime
from pytz import timezone

DATE_FORMAT = '%Y-%m-%d'


class TemplateRepository:
    def __init__(self, config):
        self._config = config

    def _build_email(self, subject, recipients, template, template_vars, csv_report=None):
        logo = 'src/templates/images/logo.png'
        header = 'src/templates/images/header.jpg'
        attachments = []

        template = os.path.join('src', 'templates', template)
        template_loader = jinja2.FileSystemLoader(searchpath='.')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template)

        if csv_report:
            attachments.append({
                'name': csv_report['name'],
                'data': base64.b64encode(csv_report['data'].encode('utf-8')).decode('utf-8')
            })

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': subject,
                'recipient': ', '.join(recipients),
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
                'attachments': attachments
            }
        }

    def _generate_csv(self, headers, rows):
        file = StringIO()
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        for row in rows:
            clean_row = [str(cell).replace('<br>', ' ') for cell in row]
            writer.writerow(clean_row)

        return file.getvalue()

    def compose_monitor_report_email(self, client_id, client_name, report_items):
        template = 'service_affecting_monitor_report.html'
        template_vars = {}
        rows = []
        headers = ['Trouble', 'Serial Number', 'Edge Name', 'Location', 'Number of tickets', 'Tickets', 'Interfaces']
        centered_headers = [4]

        for index, item in enumerate(report_items):
            rows.append([
                item['trouble'],
                item['serial_number'],
                item['edge_name'],
                '<br>'.join(item['location'].values()),
                item['number_of_tickets'],
                ',<br>'.join([str(_id) for _id in item['bruin_tickets_id']]),
                item['interfaces'],
            ])

        if rows:
            now = datetime.now(timezone(self._config.TIMEZONE))
            date = now.strftime(DATE_FORMAT)
            subject = f'{client_name} - Reoccurring Service Affecting Trouble - {date}'

            velocloud_host = self._config.VELOCLOUD_HOST
            recipients_by_host_and_client = self._config.MONITOR_REPORT_CONFIG['recipients_by_host_and_client_id']
            recipients_by_client = recipients_by_host_and_client[velocloud_host]
            recipients = self._config.MONITOR_REPORT_CONFIG['default_contacts']

            if client_id in recipients_by_client:
                recipients = recipients + recipients_by_client[client_id]

            csv_report = {
                'name': f'reoccurring-service-affecting-trouble_{date}.csv',
                'data': self._generate_csv(headers, rows)
            }

            template_vars['__DATE__'] = date
            template_vars['__YEAR__'] = now.year
            template_vars['__CLIENT_ID__'] = client_id
            template_vars['__CLIENT_NAME__'] = client_name
            template_vars['__ROWS__'] = rows
            template_vars['__HEADERS__'] = headers
            template_vars['__CENTERED_HEADERS__'] = centered_headers

            return self._build_email(subject=subject, recipients=recipients, template=template,
                                     template_vars=template_vars, csv_report=csv_report)

    def compose_bandwidth_report_email(self, client_id, client_name, report_items):
        template = 'bandwidth_report.html'
        template_vars = {}
        rows = []
        headers = ['Serial Number', 'Edge Name', 'Interface', 'Average Bandwidth',
                   'Bandwidth Trouble Threshold Exceeded', 'Bandwidth Trouble Tickets']
        centered_headers = [3, 4, 5]

        for index, item in enumerate(report_items):
            rows.append([
                item['serial_number'],
                item['edge_name'],
                item['interface'],
                item['bandwidth'],
                item['threshold_exceeded'],
                ',<br>'.join([str(_id) for _id in item['ticket_ids']]),
            ])

        if rows:
            now = datetime.now(timezone(self._config.TIMEZONE))
            date = now.strftime(DATE_FORMAT)
            subject = f'{client_name} - Daily Bandwidth Report - {date}'
            recipients = self._config.BANDWIDTH_REPORT_CONFIG['recipients']

            csv_report = {
                'name': f'daily-bandwidth-report_{date}.csv',
                'data': self._generate_csv(headers, rows)
            }

            template_vars['__DATE__'] = date
            template_vars['__YEAR__'] = now.year
            template_vars['__CLIENT_ID__'] = client_id
            template_vars['__CLIENT_NAME__'] = client_name
            template_vars['__ROWS__'] = rows
            template_vars['__HEADERS__'] = headers
            template_vars['__CENTERED_HEADERS__'] = centered_headers

            return self._build_email(subject=subject, recipients=recipients, template=template,
                                     template_vars=template_vars, csv_report=csv_report)
