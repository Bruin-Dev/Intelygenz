from unittest.mock import AsyncMock, Mock

import pytest

from application.clients.forticloud_client import ForticloudClient
from application.repositories.forticloud_repository import ForticloudRepository


@pytest.fixture(scope="function")
def forticloud_client():
    return Mock(spec_set=ForticloudClient)


@pytest.fixture(scope="function")
def forticloud_repository(forticloud_client):
    return ForticloudRepository(forticloud_client=forticloud_client)


class TestForticloudRepository:
    def instance_test(self, forticloud_repository, forticloud_client):
        assert forticloud_repository._forticloud_client is forticloud_client

    @pytest.mark.asyncio
    async def get_ap_data_test(self, forticloud_repository):
        PAYLOAD_MODEL = {
            "fields": ["name", "admin", "_conn-state"],
            "target": ["adom/production/group/All_FortiGate"],
        }
        payload = {
            "response_topic": "some_temp_topic",
            "body": {"payload": PAYLOAD_MODEL},
        }
        response = {}

        forticloud_repository._forticloud_client.get_ap_data = AsyncMock(return_value=response)

        result = await forticloud_repository.get_ap_data(payload)

        forticloud_repository._forticloud_client.get_ap_data.assert_awaited_once_with(payload)
        assert result == response

    @pytest.mark.asyncio
    async def get_switches_data_test(self, forticloud_repository):
        PAYLOAD_MODEL = {
            "fields": ["name", "switch-id", "scope member", "state", "status"],
            "target": ["adom/production/group/All_FortiGate"],
        }

        payload = {
            "response_topic": "some_temp_topic",
            "body": {"payload": PAYLOAD_MODEL},
        }
        response = {}

        forticloud_repository._forticloud_client.get_switches_data = AsyncMock(return_value=response)

        result = await forticloud_repository.get_switches_data(payload)

        forticloud_repository._forticloud_client.get_switches_data.assert_awaited_once_with(payload)
        assert result == response
