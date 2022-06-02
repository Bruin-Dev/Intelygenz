import base64
import csv
import io
from datetime import date
from os.path import join
from typing import List

import jinja2


class TemplateRenderer:
    def __init__(self, config):
        self._config = config

    def compose_email_object(self, summary: dict, data: List[dict], **opts) -> dict:
        loader = jinja2.FileSystemLoader(searchpath=".")
        environ = jinja2.Environment(loader=loader)

        template_path = join("src/templates", opts.get("template", "lumin_billing_report.html"))
        logo = join("src/templates/images", opts.get("logo", "logo.png"))
        header = join("src/templates/images", opts.get("header", "header.jpg"))
        csv_name = opts.get("csv", "lumin_billing_report")
        customer = self._config["customer_name"]

        template = environ.get_template(template_path)

        email_html = template.render(**summary)

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=self._config["fieldnames"])
        writer.writeheader()
        writer.writerows(data)

        buf.seek(0)
        raw_csv = buf.read()

        return {
            "subject": f"{customer} Lumin.AI Billing Report ({date.today()})",
            "recipient": self._config["recipient"],
            "text": "this is the accessible text for the email",
            "html": email_html,
            "images": [
                {"name": "logo", "data": base64.b64encode(open(logo, "rb").read()).decode("utf-8")},
                {"name": "header", "data": base64.b64encode(open(header, "rb").read()).decode("utf-8")},
            ],
            "attachments": [
                {
                    "name": f"{customer}-{csv_name}-{date.today()}.csv",
                    "data": base64.b64encode(raw_csv.encode("utf-8")).decode("utf-8"),
                }
            ],
        }
