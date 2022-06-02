import base64
from datetime import datetime

import jinja2
import pandas as pd
from shortuuid import uuid


class TemplateRenderer:
    def __init__(self, config):
        self._config = config

    def compose_email_object(self, edges_to_report, **kwargs):
        templateLoader = jinja2.FileSystemLoader(searchpath=".")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = "src/templates/{}".format(kwargs.get("template", "last_contact.html"))
        logo = "src/templates/images/{}".format(kwargs.get("logo", "logo.png"))
        header = "src/templates/images/{}".format(kwargs.get("header", "header.jpg"))
        csv = "{}".format(kwargs.get("csv", "last_contact.csv"))
        templ = templateEnv.get_template(template)
        template_vars = {}
        template_vars["__EDGE_COUNT__"] = str(len(edges_to_report))
        enterprises = {}
        for edge in edges_to_report:
            if edge["enterprise"] not in enterprises.keys():
                enterprises[edge["enterprise"]] = 0
            enterprises[edge["enterprise"]] += 1

        list_rows = []
        for idx, enterprise in enumerate(enterprises.keys()):
            list_rows.append(
                {
                    "type": "even" if idx % 2 == 0 else "odd",
                    "__ENTERPRISE__": enterprise,
                    "__COUNT__": str(enterprises[enterprise]),
                }
            )
        template_vars["list_row"] = list_rows
        edges_dataframe = pd.DataFrame(edges_to_report)
        file_csv = edges_dataframe.to_csv(index=False)
        file_csv = base64.b64encode(file_csv.encode("utf-8"))
        email_html = templ.render(**template_vars)

        return {
            "request_id": uuid(),
            "email_data": {
                "subject": f'Last contact edges ({datetime.now().strftime("%Y-%m-%d")})',
                "recipient": self._config["recipient"],
                "text": "this is the accessible text for the email",
                "html": email_html,
                "images": [
                    {"name": "logo", "data": base64.b64encode(open(logo, "rb").read()).decode("utf-8")},
                    {"name": "header", "data": base64.b64encode(open(header, "rb").read()).decode("utf-8")},
                ],
                "attachments": [{"name": csv, "data": file_csv.decode("utf-8")}],
            },
        }
