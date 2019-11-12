import json
import base64
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
    def __init__(self, logger, event_bus, config):
        self._logger = logger
        self._event_bus = event_bus
        self._config = config

    async def run_action(self, device, edge_status, trouble, ticket_dict):
        email_obj = self._compose_email_object(edge_status, trouble, ticket_dict)
        await self._event_bus.rpc_request("notification.email.request", json.dumps(email_obj), timeout=10)

    def _compose_email_object(self, edges_status_to_report, trouble, ticket_dict):
        with open('src/templates/service_affecting_monitor.html') as template:
            email_html = "".join(template.readlines())
            email_html = email_html.replace('%%TROUBLE%%', trouble)
            email_html = email_html.replace('%%SERIAL_NUMBER%%',
                                            f'{edges_status_to_report["edge_info"]["edges"]["serialNumber"]}')

        rows = []
        for idx, key in enumerate(ticket_dict.keys()):
            row = EVEN_ROW if idx % 2 == 0 else ODD_ROW
            row = row.replace('%%KEY%%', key)
            row = row.replace('%%VALUE%%', str(ticket_dict[key]))
            rows.append(row)
        email_html = email_html.replace('%%OVERVIEW_ROWS%%', "".join(rows))

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
