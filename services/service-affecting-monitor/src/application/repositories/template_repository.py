import base64
import csv
import os
from datetime import datetime
from io import StringIO

import jinja2
from pytz import timezone
from shortuuid import uuid

DATE_FORMAT = "%Y-%m-%d"


class TemplateRepository:
    def __init__(self, config):
        self._config = config

    @staticmethod
    def _build_email(subject, recipients, template_vars, template_name, csv_report=None):
        attachments = []

        template = "/".join(["src", "templates", template_name])
        template_loader = jinja2.FileSystemLoader(searchpath=".")
        template_env = jinja2.Environment(loader=template_loader, autoescape=True)
        template = template_env.get_template(template)

        if csv_report:
            attachments.append(
                {
                    "name": csv_report["name"],
                    "data": base64.b64encode(csv_report["data"].encode("utf-8")).decode("utf-8"),
                }
            )

        return {
            "request_id": uuid(),
            "body": {
                "email_data": {
                    "subject": subject,
                    "recipient": ", ".join(recipients),
                    "text": "",
                    "html": template.render(**template_vars),
                    "images": [
                        {
                            "name": "logo",
                            "data": base64.b64encode(open("src/templates/images/logo.png", "rb").read()).decode(
                                "utf-8"
                            ),
                        },
                        {
                            "name": "header",
                            "data": base64.b64encode(open("src/templates/images/header.jpg", "rb").read()).decode(
                                "utf-8"
                            ),
                        },
                    ],
                    "attachments": attachments,
                }
            },
        }

    @staticmethod
    def _generate_csv(headers, rows):
        file = StringIO()
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)

        for row in rows:
            clean_row = [str(cell).replace("<br>", " ") for cell in row]
            writer.writerow(clean_row)

        return file.getvalue()

    def compose_monitor_report_email(self, client_id, client_name, report_items, trailing_interval):

        rows = []
        headers = ["Trouble", "Serial Number", "Edge Name", "Location", "Number of tickets", "Tickets", "Interfaces"]
        centered_headers = [4]

        now = trailing_interval["end"]
        date = now.strftime(DATE_FORMAT)
        template_vars = {
            "__DATE__": date,
            "__YEAR__": now.year,
            "__CLIENT_ID__": client_id,
            "__CLIENT_NAME__": client_name,
        }

        recipients = self.get_recipients_for_trouble_report(client_id)

        for index, item in enumerate(report_items):
            rows.append(
                [
                    item["trouble"],
                    item["serial_number"],
                    item["edge_name"],
                    "<br>".join(item["location"].values()),
                    item["number_of_tickets"],
                    ",<br>".join([str(_id) for _id in item["bruin_tickets_id"]]),
                    item["interfaces"],
                ]
            )

        if rows:
            csv_report = {
                "name": f"reoccurring-service-affecting-trouble_{date}.csv",
                "data": self._generate_csv(headers, rows),
            }

            template_vars["__ROWS__"] = rows
            template_vars["__HEADERS__"] = headers
            template_vars["__CENTERED_HEADERS__"] = centered_headers
        else:
            template_vars["__EMPTY_CSV__"] = True
            csv_report = None

        return self._build_email(
            subject=f"{client_name} - Reoccurring Service Affecting Trouble - {date}",
            recipients=recipients,
            template_vars=template_vars,
            template_name="service_affecting_monitor_report.html",
            csv_report=csv_report,
        )

    def get_recipients_for_trouble_report(self, client_id):
        recipients_by_host_and_client = self._config.MONITOR_REPORT_CONFIG["recipients_by_host_and_client_id"]
        recipients_by_client = recipients_by_host_and_client[self._config.VELOCLOUD_HOST]
        recipients = self._config.MONITOR_REPORT_CONFIG["default_contacts"]
        if client_id in recipients_by_client:
            recipients = recipients + recipients_by_client[client_id]
        return recipients

    def get_recipients_for_bandwidth_report(self, client_id):
        recipients_by_host_and_client = self._config.BANDWIDTH_REPORT_CONFIG["recipients_by_host_and_client_id"]
        recipients_by_client = recipients_by_host_and_client[self._config.VELOCLOUD_HOST]
        recipients = self._config.BANDWIDTH_REPORT_CONFIG["default_contacts"]
        if client_id in recipients_by_client:
            recipients = recipients + recipients_by_client[client_id]
        return recipients

    def compose_bandwidth_report_email(self, client_id, client_name, report_items):
        now = datetime.now(timezone(self._config.TIMEZONE))
        date = now.strftime(DATE_FORMAT)

        recipients = self.get_recipients_for_bandwidth_report(client_id)
        subject = f"{client_name} - Daily Bandwidth Report - {date}"
        template_vars = {
            "__DATE__": date,
            "__YEAR__": now.year,
            "__CLIENT_ID__": client_id,
            "__CLIENT_NAME__": client_name,
        }
        rows = []
        headers = [
            "Enterprise Id",
            "Enterprise Name",
            "Serial Number",
            "Edge Name",
            "Interface",
            "Link Name",
            "Available Bandwidth Down Min",
            "Available Bandwidth Down Max",
            "Peak Utilization Down",
            "Peak Utilization Time Down",
            "Peak Utilization % Down",
            "Total Number: Bandwidth Threshold Exceeded Down",
            "Bandwidth Trouble Tickets Down",
            "                      ",
            "Available Bandwidth Up Min",
            "Available Bandwidth Up Max",
            "Peak Utilization Up",
            "Peak Utilization Time Up",
            "Peak Utilization % Up",
            "Total Number: Bandwidth Threshold Exceeded Up",
            "Bandwidth Trouble Tickets Up",
        ]
        centered_headers = [3, 4, 5]

        serial_number_set = set()
        for index, item in enumerate(report_items):
            serial_number_set.add(item["serial_number"])
            rows.append(
                [
                    item["enterprise_id"],
                    item["enterprise_name"],
                    item["serial_number"],
                    item["edge_name"],
                    item["interface"],
                    item["link_name"],
                    item["down_Mbps_total_min"],
                    item["down_Mbps_total_max"],
                    item["peak_Mbps_down"],
                    item["peak_time_down"],
                    item["peak_percent_down"],
                    item["threshold_exceeded_down"],
                    ", ".join([str(_id) for _id in item["ticket_ids_down"]]),
                    " ",
                    item["up_Mbps_total_min"],
                    item["up_Mbps_total_max"],
                    item["peak_Mbps_up"],
                    item["peak_time_up"],
                    item["peak_percent_up"],
                    item["threshold_exceeded_up"],
                    ", ".join([str(_id) for _id in item["ticket_ids_up"]]),
                ]
            )

        if rows:
            csv_report = {"name": f"daily-bandwidth-report_{date}.csv", "data": self._generate_csv(headers, rows)}

            template_vars["__EDGE_COUNT__"] = len(serial_number_set)
        else:
            template_vars["__EMPTY_CSV__"] = True
            csv_report = None

        return self._build_email(
            subject=subject,
            recipients=recipients,
            template_vars=template_vars,
            template_name="bandwidth_report.html",
            csv_report=csv_report,
        )
