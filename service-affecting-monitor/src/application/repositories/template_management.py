import jinja2
from shortuuid import uuid
import base64


class TemplateRenderer:
    def __init__(self, config):
        self._config = config

    def compose_email_object(self, edges_status_to_report, trouble, ticket_dict, **kwargs):
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        template_vars = {}
        template = "src/templates/{}".format(kwargs.get("template", "service_affecting_monitor.html"))
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)
        template_vars["__TROUBLE__"] = trouble
        template_vars["__SERIAL_NUMBER__"] = f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}'

        rows = []
        for idx, key in enumerate(ticket_dict.keys()):
            rows.append({
                "type": "even" if idx % 2 == 0 else "odd",
                "__KEY__": key,
                "__VALUE__": str(ticket_dict[key])
            })
        template_vars["__OVERVIEW_ROWS__"] = rows
        email_html = templ.render(**template_vars)

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Service affecting trouble detected: {trouble}',
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

    def compose_email_report_object(
            self, report: dict, report_items: list, **kwargs):
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        template_vars = {}
        template = "src/templates/{}".format(
            kwargs.get("template", "service_affecting_monitor_report.html"))
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)
        template_vars["__TROUBLE__"] = f"{report['name']}"
        template_vars["__SERIAL_NUMBERS__"] = \
            f"({len(report_items)}) {', '.join([report_item['serial_number'] for report_item in report_items])}"

        rows = []
        for idx, value in enumerate(report_items):
            rows.append({
                "type": "even" if idx % 2 == 0 else "odd",
                "__KEY__": value['serial_number'],
                "__CLIENT__": f"{value['customer']['client_id']} | {value['customer']['client_name']}",
                "__LOCATION__": f"{'<br>'.join(list(value['location'].values()))}",
                "__NUMBER_OF_TICKETS__": f"{value['number_of_tickets']}",
                "__BRUIN_TICKETS_ID__": f"{',<br>'.join([str(i) for i in value['bruin_tickets_id']])}",
                "__INTERFACES__": str(value['interfaces']),
            })
        template_vars["__OVERVIEW_ROWS__"] = rows
        email_html = templ.render(**template_vars)

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f"Service affecting bandwidth utilization for {report['trailing_days']} days",
                'recipient': report['recipient'],
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
