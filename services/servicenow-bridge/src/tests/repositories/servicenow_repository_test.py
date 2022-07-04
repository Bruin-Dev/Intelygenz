from unittest.mock import Mock

import pytest
from application.repositories.servicenow_repository import ServiceNowRepository
from asynctest import CoroutineMock


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

        payload = {
            "u_host_name": host,
            "u_vcg": gateway,
            "u_short_description": summary,
            "u_description": note,
        }

        response = {}

        servicenow_client = Mock()
        servicenow_client.report_incident = CoroutineMock(return_value=response)

        servicenow_repository = ServiceNowRepository(servicenow_client)
        result = await servicenow_repository.report_incident(host, gateway, summary, note)

        servicenow_client.report_incident.assert_awaited_once_with(payload)
        assert result == response
