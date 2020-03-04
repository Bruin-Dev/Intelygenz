import base64

from datetime import datetime

import pandas as pd
import pytz

from pytz import timezone
from shortuuid import uuid


class ComparisonReportRenderer:
    __report_template_filename = "comparison_report.html"
    __logo_path = "src/templates/images/logo.png"
    __header_path = "src/templates/images/header.jpg"

    def __init__(self, config, templates_environment):
        self._config = config
        self._templates_environment = templates_environment

    def compose_email_object(self, edges_to_report, **kwargs):
        template_vars = {}
        # This path changes if you execute it from pycharm
        date = datetime.now(pytz.timezone('US/Eastern'))
        full_date = date.strftime("%b_%d_%Y_%H-%M-%S")
        self.csv = "{}_{}.csv".format(kwargs.get("csv", "report_mail_template"), full_date)
        template_vars["__EDGE_COUNT__"] = str(len(edges_to_report))
        template_vars["__TIME_REPORT__"] = kwargs.get("time_report", "4") + " hours"
        template_vars["__FIELDS__"] = kwargs.get("fields", list(edges_to_report[0].keys()))
        template_vars["__FIELDS_REL__"] = {field: field_related for field, field_related in
                                           zip(template_vars["__FIELDS__"], kwargs.get("fields_edge"))}
        template_vars["list_row"] = []
        for idx, edge_data in enumerate(edges_to_report):
            row = {
                "type": "even" if idx % 2 == 0 else "odd",
                **edge_data
            }
            row['links'] = '<a href="{edge_url}">{edge_url}</a>'.format(edge_url=edge_data["edge_url"])

            outage_causes_elements = map(lambda cause: f'<li>{cause}</li>', edge_data["outage_causes"])
            row['outage_causes'] = f"<ul>{''.join(outage_causes_elements)}</ul>"

            template_vars["list_row"].append(row)

        for edge in edges_to_report:
            edge['outage_causes'] = ', '.join(edge['outage_causes'])

        edges_dataframe = pd.DataFrame(edges_to_report)
        file_csv = edges_dataframe.to_csv(index=False)
        file_csv = base64.b64encode(file_csv.encode("utf-8"))

        template = self._templates_environment.get_template(self.__report_template_filename)
        email_html = template.render(template_vars)
        tz = timezone(self._config.MONITOR_CONFIG['timezone'])

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Service Outage Report ({datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M")})',
                'recipient': self._config.MONITOR_CONFIG["recipient"],
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
                'attachments': [
                    {
                        'name': self.csv,
                        'data': file_csv.decode('utf-8')
                    }
                ]
            }
        }
