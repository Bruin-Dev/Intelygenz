import base64
import csv
import io

from datetime import date, timedelta

import pytest

from application.repositories.template_renderer import TemplateRenderer
from config.testconfig import BILLING_REPORT_CONFIG


@pytest.fixture
def template_data():
    items = [
        {
            "conversation_id": "5735605401026560",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
            "timestamp": "2019-02-24T21:29:36.798081+00:00",
            "type": "billing.scheduled"
        },
        {
            "conversation_id": "5711381785477120",
            "host_did": "199234567890",
            "host_id": "default",
            "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
            "timestamp": "2019-02-24T21:36:01.295808+00:00",
            "type": "billing.rescheduled"
        }
    ]

    today = date.today()
    last = date.today() - timedelta(days=1)
    first = last.replace(day=1)

    summary = {
        "dates": {
            "current": today.strftime(BILLING_REPORT_CONFIG["date_format"]),
            "start": first.strftime(BILLING_REPORT_CONFIG["date_format"]),
            "end": last.strftime(BILLING_REPORT_CONFIG["date_format"])
        },
        "total": 2,
        "type_counts": {
            "billing.scheduled": 1,
            "billing.rescheduled": 1
        }
    }

    return summary, items


class TestTemplateRenderer:

    def instantiation_test(self):
        test_repo = TemplateRenderer(BILLING_REPORT_CONFIG)
        assert test_repo._config == BILLING_REPORT_CONFIG

    def compose_email_object_test(self, template_data):
        template_renderer = TemplateRenderer(BILLING_REPORT_CONFIG)

        email = template_renderer.compose_email_object(*template_data)

        assert 'FCI Lumin.AI Billing Report' in email["subject"]
        assert BILLING_REPORT_CONFIG["recipient"] in email["recipient"]
        assert "<!DOCTYPE html" in email["html"]

    def compose_email_object_test(self, template_data):
        base = "src/templates/images/{}"
        kwargs = dict(template="lumin_billing_report.html",
                      logo="logo.png",
                      header="header.jpg")

        test_repo = TemplateRenderer(BILLING_REPORT_CONFIG)
        email = test_repo.compose_email_object(*template_data)

        assert "billing.scheduled" in email["html"]
        assert "billing.rescheduled" in email["html"]
        assert email["images"][0]["data"] == base64.b64encode(
            open(base.format(kwargs["logo"]), 'rb').read()).decode('utf-8')
        assert email["images"][1]["data"] == base64.b64encode(
            open(base.format(kwargs["header"]), 'rb').read()).decode('utf-8')

        raw_csv = base64.b64decode(email["attachments"][0]["data"].encode('utf-8')).decode('utf-8')
        reader = csv.DictReader(io.StringIO(raw_csv))

        for row in reader:
            assert all(field in row for field in BILLING_REPORT_CONFIG["fieldnames"])
