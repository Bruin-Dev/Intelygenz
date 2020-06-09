import pytest

from datetime import date, datetime, timedelta
from unittest.mock import Mock

from aioresponses import aioresponses
from asynctest import CoroutineMock
from pytz import timezone

from application.clients.lumin_client import LuminBillingClient
from application.repositories.template_renderer import TemplateRenderer
from application.repositories.lumin_repository import LuminBillingRepository
from application.actions.billing_report import BillingReport
from config import testconfig


@pytest.fixture
def mock_responses():
    tz = timezone(testconfig.BILLING_REPORT_CONFIG["timezone"])
    return [{
        "ok": True,
        "next_token": "foo",
        "items": [
            {
                "conversation_id": "5735605401026560",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
                "timestamp": str(datetime.now(tz=tz) - timedelta(days=29)),
                "type": "billing.scheduled"
            },
            {
                "conversation_id": "5711381785477120",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
                "timestamp": str(datetime.now(tz=tz) - timedelta(days=20)),
                "type": "billing.scheduled"
            }
        ]
    }, {
        "ok": True,
        "items": [
            {
                "conversation_id": "5735605401026560",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
                "timestamp": str(datetime.now(tz=tz) - timedelta(days=15)),
                "type": "billing.rescheduled"
            },
            {
                "conversation_id": "5711381785477120",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
                "timestamp": str(datetime.now(tz=tz) - timedelta(days=1)),
                "type": "billing.rescheduled"
            }
        ]
    }]


@pytest.fixture
def expected_summary():
    today = date.today()
    last = date.today() - timedelta(days=1)
    first = last.replace(day=1)

    return {
        "dates": {
            "current": today.strftime(testconfig.BILLING_REPORT_CONFIG["date_format"]),
            "start": first.strftime(testconfig.BILLING_REPORT_CONFIG["date_format"]),
            "end": last.strftime(testconfig.BILLING_REPORT_CONFIG["date_format"])
        },
        "customer": testconfig.BILLING_REPORT_CONFIG["customer_name"],
        "total_api_uses": 4,
        "type_counts": {
            "billing.scheduled": 2,
            "billing.rescheduled": 2
        }
    }


@pytest.mark.asyncio
class TestSendBillingReport:

    async def send_billing_report_test(self, mock_responses, expected_summary):
        with aioresponses() as m:
            m.post(testconfig.LUMIN_CONFIG["uri"], payload=mock_responses[0])
            m.post(testconfig.LUMIN_CONFIG["uri"], payload=mock_responses[1])

            client = LuminBillingClient(testconfig.LUMIN_CONFIG)
            repo = LuminBillingRepository(Mock(), client)
            email = Mock()
            email.send_to_email = CoroutineMock()
            templ = TemplateRenderer(testconfig.BILLING_REPORT_CONFIG)
            templ.compose_email_object = Mock(wraps=templ.compose_email_object)

            opts = {
                "logger": Mock(),
                "config": testconfig.BILLING_REPORT_CONFIG
            }

            report = BillingReport(repo, email, templ, Mock(), **opts)
            await report._billing_report_process()

            summary, items = templ.compose_email_object.call_args[0]

            assert summary == expected_summary
            assert items == mock_responses[0]["items"] + mock_responses[1]["items"]

            email_obj = email.send_to_email.call_args[0][0]

            assert email_obj["subject"] == f'{expected_summary["customer"]} Lumin.AI Billing Report ({date.today()})'
            assert email_obj["recipient"] == testconfig.BILLING_REPORT_CONFIG["recipient"]

            current = expected_summary["dates"]["current"]
            start = expected_summary["dates"]["start"]
            end = expected_summary["dates"]["end"]

            assert "<!DOCTYPE html" in email_obj["html"]
            assert f'<b>Generated</b>: {current}' in email_obj["html"]
            assert f'<b>Period</b>: {start} - {end}' in email_obj["html"]

            for r in mock_responses:
                assert all(item["type"] in email_obj["html"] for item in r["items"])

            assert len(email_obj["images"]) == 2

            expected = f'{expected_summary["customer"]}-lumin_billing_report-{date.today()}.csv'

            assert email_obj["attachments"][0]["name"] == expected
