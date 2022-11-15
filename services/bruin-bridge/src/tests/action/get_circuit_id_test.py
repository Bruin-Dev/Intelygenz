from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_circuit_id import GetCircuitID
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetCircuitID:
    def instance_test(self):
        bruin_repository = Mock()

        circuit_id_response = GetCircuitID(bruin_repository)

        assert circuit_id_response._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_circuit_id_test(self):
        circuit_id_return = {
            "body": {"clientID": "432", "subAccount": "string", "wtn": "123", "inventoryID": 0, "addressID": 0},
            "status": 200,
        }
        circuit_id = "123"

        payload = {
            "circuit_id": circuit_id,
        }
        event_bus_request = {"body": payload}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **circuit_id_return,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = AsyncMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(bruin_repository)
        await circuit_id_response(request_msg)
        bruin_repository.get_circuit_id.assert_awaited_once_with(payload)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_circuit_id_no_body_test(self):
        circuit_id_return = {"body": 'You must specify {.."body":{"circuit_id"}...} in the request', "status": 400}

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **circuit_id_return,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = AsyncMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(bruin_repository)
        await circuit_id_response(request_msg)
        bruin_repository.get_circuit_id.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def get_circuit_id_no_circuit_id_test(self):
        circuit_id_return = {"body": 'You must specify "circuit_id" in the body', "status": 400}

        payload = {}

        event_bus_request = {
            "body": payload,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **circuit_id_return,
        }

        bruin_repository = Mock()
        bruin_repository.get_circuit_id = AsyncMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(bruin_repository)
        await circuit_id_response(request_msg)
        bruin_repository.get_circuit_id.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
