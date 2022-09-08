import json
from unittest.mock import AsyncMock, Mock

import pytest

from application.actions.report_incident import ReportIncident


class TestReportIncident:
    def instance_test(self):
        nats_client = Mock()
        servicenow_repository = Mock()

        action = ReportIncident(nats_client, servicenow_repository)

        assert action._event_bus is nats_client
        assert action._servicenow_repository is servicenow_repository

    @pytest.mark.asyncio
    async def report_incident_ok_test(self, make_msg, nats_client):
        host = "mettel.velocloud.net"
        gateway = "vcg-test-1"
        summary = "Test summary"
        note = "Test note"
        link = "https://mettel.velocloud.net/#!/operator/admin/gateways/1/monitor/"

        msg_body = {
            "host": host,
            "gateway": gateway,
            "summary": summary,
            "note": note,
            "link": link,
        }

        request = {"request_id": 1, "body": msg_body}
        response = {"body": {}, "status": 200}

        servicenow_repository = Mock()

        action = ReportIncident(nats_client, servicenow_repository)
        action._servicenow_repository.report_incident = AsyncMock(return_value=response)

        msg = make_msg(request)
        msg.respond = AsyncMock()
        await action(msg)
        servicenow_repository.report_incident.assert_awaited_once_with(host, gateway, summary, note, link)
        msg.respond.assert_awaited_once_with(json.dumps(response).encode())

    @pytest.mark.asyncio
    async def report_incident_400_no_body_test(self, make_msg, nats_client):
        request = {"request_id": 1}

        response = {
            "request_id": 1,
            "body": 'Must include "body" in the request',
            "status": 400,
        }

        servicenow_repository = Mock()
        action = ReportIncident(nats_client, servicenow_repository)

        msg = make_msg(request)
        msg.respond = AsyncMock()
        await action(msg)
        msg.respond.assert_awaited_once_with(json.dumps(response).encode())

    @pytest.mark.asyncio
    async def report_incident_400_body_with_missing_fields_test(self, make_msg, nats_client):
        request = {"request_id": 1, "body": {}}

        response = {
            "request_id": 1,
            "body": 'You must include "host", "gateway", "summary", "note" and "link" in the request body',
            "status": 400,
        }

        servicenow_repository = Mock()

        action = ReportIncident(nats_client, servicenow_repository)

        msg = make_msg(request)
        msg.respond = AsyncMock()
        await action(msg)
        msg.respond.assert_awaited_once_with(json.dumps(response).encode())
