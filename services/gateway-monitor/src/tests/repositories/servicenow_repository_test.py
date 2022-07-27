import os
from http import HTTPStatus
from unittest.mock import patch

import pytest
from application.repositories import servicenow_repository as servicenow_repository_module
from asynctest import CoroutineMock, Mock
from config import testconfig
from shortuuid import uuid
from tests.fixtures._constants import CURRENT_DATETIME

uuid_ = uuid()
uuid_mock = patch.object(servicenow_repository_module, "uuid", return_value=uuid_)


class TestServiceNowRepository:
    def instance_test(self, servicenow_repository, event_bus, logger, notifications_repository):
        assert servicenow_repository._event_bus is event_bus
        assert servicenow_repository._logger is logger
        assert servicenow_repository._notifications_repository is notifications_repository
        assert servicenow_repository._config is testconfig

    def build_incident_summary_test(self, servicenow_repository, make_gateway):
        gateway = make_gateway(id=1)
        result = servicenow_repository._build_incident_summary(gateway)
        assert result == "vcg-test-1: Medium: VCG Tunnel Count Threshold Violation"

    def build_incident_note_test(self, servicenow_repository, make_gateway_with_metrics):
        gateway = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 50})
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)

        with patch.object(servicenow_repository_module, "datetime", new=datetime_mock):
            note = servicenow_repository._build_incident_note(gateway)

        assert note == os.linesep.join(
            [
                f"VCO: mettel.velocloud.net",
                f"VCG: vcg-test-1",
                "",
                f"Condition: Over 20% reduction in tunnel count compared to average",
                f"Minimum Tunnel Count: 50",
                f"Average Tunnel Count: 100",
                f"Scan Interval: 60 minutes",
                "",
                f"TimeStamp: {CURRENT_DATETIME}",
            ]
        )

    def build_incident_link_test(self, servicenow_repository, make_gateway):
        gateway = make_gateway(id=1)
        result = servicenow_repository._build_incident_link(gateway)
        assert result == "https://mettel.velocloud.net/#!/operator/admin/gateways/1/monitor/"

    @pytest.mark.asyncio
    async def report_incident_test(
        self,
        servicenow_repository,
        make_gateway_with_metrics,
        make_rpc_request,
        make_rpc_response,
    ):
        gateway = make_gateway_with_metrics(id=1, tunnel_count={"average": 100, "min": 50})
        summary = "Test summary"
        note = "Test note"
        link = "https://mettel.velocloud.net/#!/operator/admin/gateways/1/monitor/"

        payload = {
            "host": gateway["host"],
            "gateway": gateway["name"],
            "summary": summary,
            "note": note,
            "link": link,
        }

        request = make_rpc_request(request_id=uuid_, body=payload)
        response = make_rpc_response(request_id=uuid_, body=None, status=HTTPStatus.OK)

        servicenow_repository._build_incident_summary.return_value = summary
        servicenow_repository._build_incident_note.return_value = note
        servicenow_repository._event_bus.rpc_request = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await servicenow_repository.report_incident(gateway)

        servicenow_repository._build_incident_summary.assert_called_once_with(gateway)
        servicenow_repository._build_incident_note.assert_called_once_with(gateway)
        servicenow_repository._event_bus.rpc_request.assert_awaited_once_with(
            "servicenow.incident.report.request", request, timeout=30
        )
        assert result == response
