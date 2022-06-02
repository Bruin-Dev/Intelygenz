from unittest.mock import Mock

import pytest
from application.actions.get_circuit_id import GetCircuitID
from asynctest import CoroutineMock


class TestGetCircuitID:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        circuit_id_response = GetCircuitID(logger, event_bus, bruin_repository)

        assert circuit_id_response._logger is logger
        assert circuit_id_response._event_bus is event_bus
        assert circuit_id_response._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_circuit_id_test(self):
        circuit_id_return = {
            "body": {"clientID": "432", "subAccount": "string", "wtn": "123", "inventoryID": 0, "addressID": 0},
            "status": 200,
        }
        circuit_id = "123"
        client_id = "321"

        payload = {
            "circuit_id": circuit_id,
        }
        event_bus_request = {"request_id": 19, "body": payload, "response_topic": "some.topic"}

        event_bus_response = {
            "request_id": 19,
            **circuit_id_return,
        }

        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(logger, event_bus, bruin_repository)
        await circuit_id_response.get_circuit_id(event_bus_request)
        bruin_repository.get_circuit_id.assert_awaited_once_with(payload)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        logger.info.assert_called()

    @pytest.mark.asyncio
    async def get_circuit_id_no_body_test(self):
        circuit_id_return = {"body": 'You must specify {.."body":{"circuit_id"}...} in the request', "status": 400}
        circuit_id = "123"
        client_id = "321"

        payload = {
            "circuit_id": circuit_id,
        }
        event_bus_request = {"request_id": 19, "response_topic": "some.topic"}

        event_bus_response = {
            "request_id": 19,
            **circuit_id_return,
        }

        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(logger, event_bus, bruin_repository)
        await circuit_id_response.get_circuit_id(event_bus_request)
        bruin_repository.get_circuit_id.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def get_circuit_id_no_circuit_id_test(self):
        circuit_id_return = {"body": 'You must specify "circuit_id" in the body', "status": 400}

        payload = {}

        event_bus_request = {"request_id": 19, "body": payload, "response_topic": "some.topic"}

        event_bus_response = {
            "request_id": 19,
            **circuit_id_return,
        }

        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.get_circuit_id = CoroutineMock(return_value=circuit_id_return)

        circuit_id_response = GetCircuitID(logger, event_bus, bruin_repository)
        await circuit_id_response.get_circuit_id(event_bus_request)
        bruin_repository.get_circuit_id.assert_not_awaited()
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        logger.error.assert_called()
