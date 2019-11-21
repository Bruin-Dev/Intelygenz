import jinja2
from shortuuid import uuid
from datetime import datetime, timedelta
import base64
import pandas as pd
import pytz
import datetime


class ServiceOutageReportTemplateRenderer:

    def __init__(self, config):
        self._config = config

    def _compose_email_object(self, edges_to_report, **kwargs):
        template_vars = {}
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        template = "src/templates/{}".format(kwargs.get("template", "report_mail_template.html"))
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        date = datetime.now(pytz.timezone('US/Eastern'))
        full_date = date.strftime("%b_%d_%Y_%H:%M:%S")
        csv = "{}_{}.csv".format(kwargs.get("csv", "report_mail_template"), full_date)
        templateEnv = jinja2.Environment(loader=templateLoader)
        templ = templateEnv.get_template(template)

        template_vars["__EDGE_COUNT__"] = str(len(edges_to_report))
        template_vars["__TIME_REPORT__"] = kwargs.get("time_report", "60") + " minutes"
        template_vars["__FIELDS__"] = kwargs.get("fields", list(edges_to_report[0].keys()))
        template_vars["__FIELDS_REL__"] = {field: field_related for field, field_related in
                                           zip(template_vars["__FIELDS__"], kwargs.get("fields_edge"))}
        list_rows = []
        for idx, edge in enumerate(edges_to_report):
            list_rows.append({
                "type": "even" if idx % 2 == 0 else "odd",
                **edge
            })
            list_rows[-1]["links"] = "<br/>".join(f"<a href=\"{i}\">{i}</a>" for i in
                                                  list_rows[-1]["links"].split(" - "))
        template_vars["list_row"] = list_rows
        edges_dataframe = pd.DataFrame(edges_to_report)
        edges_dataframe.index.name = 'idx'
        edges_dataframe.to_csv(csv, index=False)
        email_html = templ.render(**template_vars)

        return {
            'request_id': uuid(),
            'email_data': {
                'subject': f'Service Outage Report ({datetime.now().strftime("%Y-%m-%d")})',
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
                'attachments': [
                    {
                        'name': csv,
                        'data': base64.b64encode(open(csv, 'rb').read()).decode('utf-8')
                    }
                ]
            }
        }
