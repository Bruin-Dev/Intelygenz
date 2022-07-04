from unittest.mock import Mock

import pytest
from application.actions.report_incident import ReportIncident
from asynctest import CoroutineMock


class TestReportIncident:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        servicenow_repository = Mock()

        action = ReportIncident(logger, event_bus, servicenow_repository)

        assert action._logger is logger
        assert action._event_bus is event_bus
        assert action._servicenow_repository is servicenow_repository

    @pytest.mark.asyncio
    async def report_incident_ok_test(self):
        host = "mettel.velocloud.net"
        gateway = "vcg-test-1"
        summary = "Test summary"
        note = "Test note"

        msg_body = {
            "host": host,
            "gateway": gateway,
            "summary": summary,
            "note": note,
        }

        request = {"request_id": 1, "body": msg_body, "response_topic": "some.topic"}
        response = {"body": {}, "status": 200}

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        servicenow_repository = Mock()

        action = ReportIncident(logger, event_bus, servicenow_repository)
        action._servicenow_repository.report_incident = CoroutineMock(return_value=response)

        await action.report_incident(request)
        servicenow_repository.report_incident.assert_awaited_once_with(host, gateway, summary, note)
        event_bus.publish_message.assert_awaited_once_with("some.topic", response)

    @pytest.mark.asyncio
    async def report_incident_400_no_body_test(self):
        request = {"request_id": 1, "response_topic": "some.topic"}

        response = {
            "request_id": 1,
            "body": 'Must include "body" in the request',
            "status": 400,
        }

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        servicenow_repository = Mock()

        action = ReportIncident(logger, event_bus, servicenow_repository)

        await action.report_incident(request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", response)

    @pytest.mark.asyncio
    async def report_incident_400_body_with_missing_fields_test(self):
        request = {"request_id": 1, "response_topic": "some.topic", "body": {}}

        response = {
            "request_id": 1,
            "body": 'You must include "host", "gateway", "summary" and "note" in the request body',
            "status": 400,
        }

        logger = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        servicenow_repository = Mock()

        action = ReportIncident(logger, event_bus, servicenow_repository)

        await action.report_incident(request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", response)
