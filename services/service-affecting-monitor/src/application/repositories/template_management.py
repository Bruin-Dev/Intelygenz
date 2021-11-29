import jinja2
from shortuuid import uuid
from datetime import datetime
from pytz import timezone

import base64


class TemplateRenderer:
    def __init__(self, config):
        self._config = config

    @staticmethod
    def build_email(logo, header, subject, recipient, html):
        return {
            'request_id': uuid(),
            'email_data': {
                'subject': subject,
                'recipient': recipient,
                'text': 'this is the accessible text for the email',
                'html': html,
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

    def compose_email_report_object(self, client_name, client_id, report_items: list, **kwargs):
        template_vars = {}
        reports_config = self._config.MONITOR_REPORT_CONFIG
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        template = "src/templates/{}".format(
            kwargs.get("template", "service_affecting_monitor_report.html"))

        recipient_list = reports_config['report_config_by_trouble']['default']
        if client_id in reports_config['report_config_by_trouble'].keys():
            recipient_list = recipient_list + reports_config['report_config_by_trouble'][client_id]

        recipient_list = ', '.join(recipient_list)

        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)
        serials = set()
        rows = []
        for idx, value in enumerate(report_items):
            row_dict = {
                "type": "even" if idx % 2 == 0 else "odd",
                "__KEY__": value['serial_number'],
                "__CLIENT__": f"{value['customer']['client_id']} | {value['customer']['client_name']}",
                "__EDGE_NAME__": value['edge_name'],
                "__LOCATION__": f"{'<br>'.join(list(value['location'].values()))}",
                "__NUMBER_OF_TICKETS__": f"{value['number_of_tickets']}",
                "__BRUIN_TICKETS_ID__": f"{',<br>'.join([str(i) for i in value['bruin_tickets_id']])}",
                "__INTERFACES__": str(value['interfaces']),
            }
            serials.add(value['serial_number'])
            row_dict["__TROUBLE__"] = str(value['trouble'])
            rows.append(row_dict)
        template_vars["__SERIAL_NUMBERS__"] = f"({len(serials)}) {', '.join(serials)}"
        if len(rows) > 0:
            date = datetime.now(timezone(self._config.MONITOR_REPORT_CONFIG['timezone'])).strftime('%Y-%m-%d')
            year = datetime.now(timezone(self._config.MONITOR_REPORT_CONFIG['timezone'])).strftime('%Y')
            template_vars["__OVERVIEW_ROWS__"] = rows
            template_vars["__DATE__"] = date
            template_vars["__YEAR__"] = year
            template_vars["__CLIENT_NAME__"] = client_name
            template_vars["__CLIENT_ID__"] = client_id
            email_html = templ.render(**template_vars)
            email = self.build_email(logo=logo, header=header,
                                     subject=f"{client_name} - Reoccurring Service Affecting Trouble - "
                                             f"{date}",
                                     recipient=recipient_list,
                                     html=email_html)
            return email
        return []
