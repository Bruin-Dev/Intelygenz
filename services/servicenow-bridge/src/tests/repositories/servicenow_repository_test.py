from unittest.mock import AsyncMock, Mock

import pytest

from application.repositories.servicenow_repository import ServiceNowRepository


class TestServiceNowRepository:
    def instance_test(self):
        servicenow_client = Mock()
        servicenow_repository = ServiceNowRepository(servicenow_client)

        assert servicenow_repository._servicenow_client is servicenow_client

    @pytest.mark.asyncio
    async def report_incident_test(self):
        host = "mettel.velocloud.net"
        gateway = "vcg-test-1"
        summary = "Test summary"
        note = "Test note"
        link = "https://mettel.velocloud.net/#!/operator/admin/gateways/1/monitor/"

        payload = {
            "u_host_name": host,
            "u_vcg": gateway,
            "u_short_description": summary,
            "u_description": note,
            "u_link": link,
        }

        response = {}

        servicenow_client = Mock()
        servicenow_client.report_incident = AsyncMock(return_value=response)

        servicenow_repository = ServiceNowRepository(servicenow_client)
        result = await servicenow_repository.report_incident(host, gateway, summary, note, link)

        servicenow_client.report_incident.assert_awaited_once_with(payload)
        assert result == response
