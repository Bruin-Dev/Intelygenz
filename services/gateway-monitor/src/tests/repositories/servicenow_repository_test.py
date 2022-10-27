import json
import os
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application import Troubles
from application.repositories import servicenow_repository as servicenow_repository_module
from config import testconfig
from tests.fixtures._constants import CURRENT_DATETIME

uuid_ = uuid()
uuid_mock = patch.object(servicenow_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestServiceNowRepository:
    def instance_test(self, servicenow_repository, nats_client, notifications_repository):
        assert servicenow_repository._nats_client is nats_client
        assert servicenow_repository._notifications_repository is notifications_repository
        assert servicenow_repository._config is testconfig

    def build_incident_summary_test(self, servicenow_repository, make_gateway):
        gateway = make_gateway(id=1, trouble=Troubles.OFFLINE)
        result = servicenow_repository._build_incident_summary(gateway)
        assert result == "vcg-test-1: VCG Offline"

        gateway = make_gateway(id=2, trouble=Troubles.TUNNEL_COUNT)
        result = servicenow_repository._build_incident_summary(gateway)
        assert result == "vcg-test-2: VCG Tunnel Count Threshold Violation"

    def build_incident_note_test(self, servicenow_repository, make_gateway):
        gateway = make_gateway(id=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)

        servicenow_repository._get_trouble_note_lines = Mock(return_value=["Condition: Test"])

        with patch.object(servicenow_repository_module, "datetime", new=datetime_mock):
            note = servicenow_repository._build_incident_note(gateway)

        assert note == os.linesep.join(
            [
                f"VCO: mettel.velocloud.net",
                f"VCG: vcg-test-1",
                "",
                f"Condition: Test",
                "",
                f"TimeStamp: {CURRENT_DATETIME}",
            ]
        )

    def get_trouble_note_lines_test(self, servicenow_repository, make_gateway_with_metrics):
        gateway = make_gateway_with_metrics(id=1, trouble=Troubles.OFFLINE)
        result = servicenow_repository._get_trouble_note_lines(gateway)
        assert result == [
            f"Condition: Gateway is offline",
        ]

        gateway = make_gateway_with_metrics(
            id=2, tunnel_count={"average": 100, "min": 50}, trouble=Troubles.TUNNEL_COUNT
        )
        result = servicenow_repository._get_trouble_note_lines(gateway)
        assert result == [
            f"Condition: Over 20% reduction in tunnel count compared to average",
            f"Minimum Tunnel Count: 50",
            f"Average Tunnel Count: 100",
            f"Scan Interval: 60 minutes",
        ]

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
        gateway = make_gateway_with_metrics(
            id=1,
            tunnel_count={"average": 100, "min": 50},
            trouble=Troubles.TUNNEL_COUNT,
        )
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
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))

        servicenow_repository._build_incident_summary = Mock(return_value=summary)
        servicenow_repository._build_incident_note = Mock(return_value=note)
        servicenow_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await servicenow_repository.report_incident(gateway)

        servicenow_repository._build_incident_summary.assert_called_once_with(gateway)
        servicenow_repository._build_incident_note.assert_called_once_with(gateway)
        servicenow_repository._nats_client.request.assert_awaited_once_with(
            "servicenow.incident.report.request", to_json_bytes(request), timeout=90
        )
        assert result == response
