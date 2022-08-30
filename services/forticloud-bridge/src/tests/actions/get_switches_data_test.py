import json
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_switches_data import GetSwitchesData
from application.repositories.forticloud_repository import ForticloudRepository


@pytest.fixture(scope="function")
def forticloud_repository():
    return Mock(spec_set=ForticloudRepository)


@pytest.fixture(scope="function")
def action(forticloud_repository):
    return GetSwitchesData(forticloud_repository=forticloud_repository)


class TestGetApData:
    @pytest.mark.asyncio
    async def instance_test(self, action, forticloud_repository):
        assert action._forticloud_repository is forticloud_repository

    @pytest.mark.asyncio
    async def get_switches_data_ok_test(self, action):
        PAYLOAD_MODEL = {
            "fields": ["name", "switch-id", "scope member", "state", "status"],
            "target": ["adom/production/group/All_FortiGate"],
        }

        request = {"request_id": 1, "body": {"payload": PAYLOAD_MODEL}, "response_topic": "some.topic"}
        expected_response = {"body": {}, "status": HTTPStatus.OK}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(request).encode()

        action._forticloud_repository.get_switches_data = AsyncMock(return_value=expected_response)

        await action(msg=msg_mock)

        action._forticloud_repository.get_switches_data.assert_awaited_once_with(payload=PAYLOAD_MODEL)
        msg_mock.respond.assert_awaited_once_with(json.dumps(expected_response).encode())

    @pytest.mark.asyncio
    async def report_incident_400_no_body_test(self, action):
        request = {"request_id": 1, "response_topic": "some.topic"}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(request).encode()

        expected_response = {
            "body": 'Must include "body" in request',
            "status": 400,
        }

        action._forticloud_repository.get_switches_data = AsyncMock(return_value=expected_response)

        await action(msg=msg_mock)

        msg_mock.respond.assert_awaited_once_with(json.dumps(expected_response).encode())

    @pytest.mark.asyncio
    async def report_incident_400_body_with_missing_fields_test(self, action):
        request = {"request_id": 1, "response_topic": "some.topic", "body": {}}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(request).encode()
        PAYLOAD_MODEL = {
            "fields": ["name", "switch-id", "scope member", "state", "status"],
            "target": ["adom/production/group/All_FortiGate"],
        }

        REQUEST_MODEL = {
            "response_topic": "some_temp_topic",
            "body": {"payload": PAYLOAD_MODEL},
        }

        expected_response = {
            "body": f"Request's should look like {REQUEST_MODEL}",
            "status": 400,
        }

        action._forticloud_repository.get_switches_data = AsyncMock(return_value=expected_response)

        await action(msg=msg_mock)

        msg_mock.respond.assert_awaited_once_with(json.dumps(expected_response).encode())
